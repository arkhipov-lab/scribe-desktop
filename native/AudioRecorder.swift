import AVFoundation
import CoreMedia
import Darwin
import Foundation
import ScreenCaptureKit

/// Dual-source recorder: system audio (ScreenCaptureKit) + microphone.
/// Usage: AudioRecorder --output /path/to/file.m4a
/// Stop: write "STOP\n" to stdin, or send SIGINT/SIGTERM.
@main
struct AudioRecorderMain {
    static func main() async {
        let args = CommandLine.arguments
        guard let outIndex = args.firstIndex(of: "--output"), outIndex + 1 < args.count else {
            fputs("Usage: AudioRecorder --output /path/to/file.m4a\n", stderr)
            exit(2)
        }
        let outputURL = URL(fileURLWithPath: args[outIndex + 1])

        let recorder = DualAudioRecorder()
        do {
            try await recorder.start(outputURL: outputURL)
            fputs("READY\n", stdout)
            fflush(stdout)
            await recorder.waitUntilStopped()
            try await recorder.stop()
            fputs("DONE\n", stdout)
            fflush(stdout)
            exit(0)
        } catch {
            fputs("ERROR: \(error.localizedDescription)\n", stderr)
            exit(1)
        }
    }
}

final class DualAudioRecorder: NSObject, SCStreamOutput, SCStreamDelegate, @unchecked Sendable {
    private var stream: SCStream?
    private var writer: AVAssetWriter?
    private var systemInput: AVAssetWriterInput?
    private var micInput: AVAssetWriterInput?
    private var sessionStarted = false
    private let audioQueue = DispatchQueue(label: "local.scribe.audio")
    private let micQueue = DispatchQueue(label: "local.scribe.mic")
    private let stopLock = NSLock()
    private var stopContinuation: CheckedContinuation<Void, Never>?
    private var stopping = false
    private var stopRequested = false
    private var signalSources: [DispatchSourceSignal] = []

    func start(outputURL: URL) async throws {
        if FileManager.default.fileExists(atPath: outputURL.path) {
            try FileManager.default.removeItem(at: outputURL)
        }

        let content = try await SCShareableContent.excludingDesktopWindows(
            false,
            onScreenWindowsOnly: true
        )
        guard let display = content.displays.first else {
            throw RecorderError.noDisplay
        }

        let filter = SCContentFilter(
            display: display,
            excludingApplications: [],
            exceptingWindows: []
        )

        let config = SCStreamConfiguration()
        config.capturesAudio = true
        config.sampleRate = 48_000
        config.channelCount = 2
        config.excludesCurrentProcessAudio = true
        config.width = 2
        config.height = 2
        config.minimumFrameInterval = CMTime(value: 1, timescale: 1)
        config.showsCursor = false

        if #available(macOS 15.0, *) {
            config.captureMicrophone = true
            if let micID = AVCaptureDevice.default(for: .audio)?.uniqueID {
                config.microphoneCaptureDeviceID = micID
            }
        }

        let writer = try AVAssetWriter(url: outputURL, fileType: .m4a)
        let systemInput = AVAssetWriterInput(
            mediaType: .audio,
            outputSettings: [
                AVFormatIDKey: kAudioFormatMPEG4AAC,
                AVSampleRateKey: 48_000,
                AVNumberOfChannelsKey: 2,
                AVEncoderBitRateKey: 128_000,
            ]
        )
        systemInput.expectsMediaDataInRealTime = true

        let micInput = AVAssetWriterInput(
            mediaType: .audio,
            outputSettings: [
                AVFormatIDKey: kAudioFormatMPEG4AAC,
                AVSampleRateKey: 48_000,
                AVNumberOfChannelsKey: 2,
                AVEncoderBitRateKey: 96_000,
            ]
        )
        micInput.expectsMediaDataInRealTime = true

        guard writer.canAdd(systemInput), writer.canAdd(micInput) else {
            throw RecorderError.writerSetupFailed
        }
        writer.add(systemInput)
        writer.add(micInput)
        guard writer.startWriting() else {
            throw writer.error ?? RecorderError.writerSetupFailed
        }

        self.writer = writer
        self.systemInput = systemInput
        self.micInput = micInput

        let stream = SCStream(filter: filter, configuration: config, delegate: self)
        try stream.addStreamOutput(self, type: .screen, sampleHandlerQueue: nil)
        try stream.addStreamOutput(self, type: .audio, sampleHandlerQueue: audioQueue)
        if #available(macOS 15.0, *) {
            try stream.addStreamOutput(self, type: .microphone, sampleHandlerQueue: micQueue)
        }
        try await stream.startCapture()
        self.stream = stream

        setupStopSources()
    }

    func waitUntilStopped() async {
        await withCheckedContinuation { (cont: CheckedContinuation<Void, Never>) in
            stopLock.lock()
            if stopRequested {
                stopLock.unlock()
                cont.resume()
                return
            }
            stopContinuation = cont
            stopLock.unlock()
        }
    }

    func stop() async throws {
        stopLock.lock()
        let already = stopping
        stopping = true
        stopLock.unlock()
        if already { return }

        for source in signalSources {
            source.cancel()
        }
        signalSources.removeAll()

        try? await stream?.stopCapture()
        stream = nil

        systemInput?.markAsFinished()
        micInput?.markAsFinished()

        if let writer {
            await withCheckedContinuation { (cont: CheckedContinuation<Void, Never>) in
                writer.finishWriting {
                    cont.resume()
                }
            }
            if writer.status == .failed {
                throw writer.error ?? RecorderError.writerFailed
            }
        }
        writer = nil
        systemInput = nil
        micInput = nil
        sessionStarted = false
    }

    private func requestStop() {
        stopLock.lock()
        stopRequested = true
        let cont = stopContinuation
        stopContinuation = nil
        stopLock.unlock()
        cont?.resume()
    }

    private func setupStopSources() {
        signal(SIGINT, SIG_IGN)
        signal(SIGTERM, SIG_IGN)

        for sig in [SIGINT, SIGTERM] {
            let source = DispatchSource.makeSignalSource(signal: sig, queue: .global())
            source.setEventHandler { [weak self] in
                self?.requestStop()
            }
            source.resume()
            signalSources.append(source)
        }

        DispatchQueue.global(qos: .utility).async { [weak self] in
            while let line = readLine(strippingNewline: true) {
                if line.trimmingCharacters(in: .whitespacesAndNewlines).uppercased() == "STOP" {
                    self?.requestStop()
                    break
                }
            }
        }
    }

    func stream(
        _ stream: SCStream,
        didOutputSampleBuffer sampleBuffer: CMSampleBuffer,
        of type: SCStreamOutputType
    ) {
        guard sampleBuffer.isValid else { return }

        switch type {
        case .audio:
            append(sampleBuffer, to: systemInput, startSessionIfNeeded: true)
        case .microphone:
            append(sampleBuffer, to: micInput, startSessionIfNeeded: false)
        case .screen:
            return
        @unknown default:
            return
        }
    }

    private func append(
        _ sampleBuffer: CMSampleBuffer,
        to input: AVAssetWriterInput?,
        startSessionIfNeeded: Bool
    ) {
        guard let input, let writer, writer.status == .writing else { return }

        if startSessionIfNeeded && !sessionStarted {
            writer.startSession(atSourceTime: sampleBuffer.presentationTimeStamp)
            sessionStarted = true
        }
        guard sessionStarted else { return }
        guard input.isReadyForMoreMediaData else { return }
        _ = input.append(sampleBuffer)
    }

    func stream(_ stream: SCStream, didStopWithError error: Error) {
        fputs("ERROR: \(error.localizedDescription)\n", stderr)
        requestStop()
    }
}

enum RecorderError: LocalizedError {
    case noDisplay
    case writerSetupFailed
    case writerFailed

    var errorDescription: String? {
        switch self {
        case .noDisplay:
            return "No display available for system audio capture."
        case .writerSetupFailed:
            return "Could not set up the audio writer."
        case .writerFailed:
            return "Audio writer failed."
        }
    }
}
