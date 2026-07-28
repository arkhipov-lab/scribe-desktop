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
    private enum Track: Hashable {
        case system
        case mic
    }

    private var stream: SCStream?
    private var writer: AVAssetWriter?
    private var systemInput: AVAssetWriterInput?
    private var micInput: AVAssetWriterInput?
    private var sessionStarted = false
    private var micCaptureEnabled = false

    /// Serializes writer/session/queue mutations (mic and system arrive on different SCStream queues).
    private let writerQueue = DispatchQueue(label: "local.scribe.writer")
    private let audioQueue = DispatchQueue(label: "local.scribe.audio")
    private let micQueue = DispatchQueue(label: "local.scribe.mic")

    private var pending: [Track: [CMSampleBuffer]] = [.system: [], .mic: []]
    private var firstPTS: [Track: CMTime] = [:]
    private var droppedNotReady: [Track: Int] = [.system: 0, .mic: 0]
    private var droppedOverflow: [Track: Int] = [.system: 0, .mic: 0]
    private var droppedAtStop: [Track: Int] = [.system: 0, .mic: 0]
    private var sessionStartWorkItem: DispatchWorkItem?

    private let maxPendingPerTrack = 240
    /// If the second track never arrives (permissions / older OS), start with what we have.
    private let sessionStartTimeoutMs = 400
    /// After capture stops, retry flushing pending samples before markAsFinished.
    private let stopDrainAttempts = 40
    private let stopDrainIntervalMs = 25

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
            micCaptureEnabled = true
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

        // Finish on the writer queue so pending samples flush before markAsFinished.
        await withCheckedContinuation { (cont: CheckedContinuation<Void, Never>) in
            writerQueue.async {
                self.sessionStartWorkItem?.cancel()
                self.sessionStartWorkItem = nil
                self.drainPendingAtStop()
                cont.resume()
            }
        }

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
        pending = [.system: [], .mic: []]
        firstPTS = [:]
        droppedAtStop = [.system: 0, .mic: 0]
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

        let track: Track
        switch type {
        case .audio:
            track = .system
        case .microphone:
            track = .mic
        case .screen:
            return
        @unknown default:
            return
        }

        writerQueue.async {
            self.handleSample(sampleBuffer, track: track)
        }
    }

    private func handleSample(_ sampleBuffer: CMSampleBuffer, track: Track) {
        guard writer?.status == .writing else { return }

        if firstPTS[track] == nil {
            firstPTS[track] = sampleBuffer.presentationTimeStamp
            armSessionStartTimeoutIfNeeded()
        }

        enqueue(sampleBuffer, track: track)

        if !sessionStarted {
            startSessionIfPossible(force: false)
        }
        if sessionStarted {
            flushPending(track: .system)
            flushPending(track: .mic)
        }
    }

    private func armSessionStartTimeoutIfNeeded() {
        guard sessionStartWorkItem == nil else { return }
        let work = DispatchWorkItem { [weak self] in
            self?.startSessionIfPossible(force: true)
            if let self, self.sessionStarted {
                self.flushPending(track: .system)
                self.flushPending(track: .mic)
            }
        }
        sessionStartWorkItem = work
        writerQueue.asyncAfter(
            deadline: .now() + .milliseconds(sessionStartTimeoutMs),
            execute: work
        )
    }

    private func startSessionIfPossible(force: Bool) {
        guard !sessionStarted, let writer, writer.status == .writing else { return }

        let hasSystem = firstPTS[.system] != nil
        let hasMic = firstPTS[.mic] != nil

        if micCaptureEnabled {
            if !(hasSystem && hasMic) && !force {
                return
            }
            if !hasSystem && !hasMic {
                return
            }
        } else if !hasSystem {
            return
        }

        var start = CMTime.invalid
        if let sys = firstPTS[.system] {
            start = sys
        }
        if let mic = firstPTS[.mic] {
            start = start.isValid ? CMTimeMinimum(start, mic) : mic
        }
        guard start.isValid else { return }

        writer.startSession(atSourceTime: start)
        sessionStarted = true
        sessionStartWorkItem?.cancel()
        sessionStartWorkItem = nil

        let sysMs = firstPTS[.system].map { Int(($0.seconds * 1000).rounded()) } ?? -1
        let micMs = firstPTS[.mic].map { Int(($0.seconds * 1000).rounded()) } ?? -1
        let startMs = Int((start.seconds * 1000).rounded())
        let deltaMs = (sysMs >= 0 && micMs >= 0) ? abs(sysMs - micMs) : -1
        fputs(
            "DIAG: session_start_ms=\(startMs) first_system_ms=\(sysMs) first_mic_ms=\(micMs) "
                + "first_delta_ms=\(deltaMs) forced=\(force)\n",
            stderr
        )
    }

    private func enqueue(_ sampleBuffer: CMSampleBuffer, track: Track) {
        var queue = pending[track] ?? []
        if queue.count >= maxPendingPerTrack {
            queue.removeFirst()
            droppedOverflow[track, default: 0] += 1
        }
        queue.append(sampleBuffer)
        pending[track] = queue
    }

    /// Retry-flush pending samples after capture stops; count any leftovers as stop drops.
    private func drainPendingAtStop() {
        if !sessionStarted {
            startSessionIfPossible(force: true)
        }
        guard sessionStarted else {
            let sysLeft = pending[.system]?.count ?? 0
            let micLeft = pending[.mic]?.count ?? 0
            if sysLeft > 0 {
                droppedAtStop[.system, default: 0] += sysLeft
                pending[.system] = []
            }
            if micLeft > 0 {
                droppedAtStop[.mic, default: 0] += micLeft
                pending[.mic] = []
            }
            logDropDiagnostics()
            return
        }

        for _ in 0..<stopDrainAttempts {
            flushPending(track: .system)
            flushPending(track: .mic)
            let remaining =
                (pending[.system]?.count ?? 0) + (pending[.mic]?.count ?? 0)
            if remaining == 0 {
                break
            }
            Thread.sleep(forTimeInterval: Double(stopDrainIntervalMs) / 1000.0)
        }

        for track in [Track.system, Track.mic] {
            let left = pending[track]?.count ?? 0
            if left > 0 {
                droppedAtStop[track, default: 0] += left
                pending[track] = []
            }
        }
        logDropDiagnostics()
    }

    private func flushPending(track: Track) {
        guard sessionStarted else { return }
        let input: AVAssetWriterInput?
        switch track {
        case .system:
            input = systemInput
        case .mic:
            input = micInput
        }
        guard let input else { return }

        var queue = pending[track] ?? []
        while let sample = queue.first {
            guard input.isReadyForMoreMediaData else { break }
            if input.append(sample) {
                queue.removeFirst()
            } else {
                droppedNotReady[track, default: 0] += 1
                break
            }
        }
        pending[track] = queue
    }

    private func logDropDiagnostics() {
        let sysNR = droppedNotReady[.system] ?? 0
        let micNR = droppedNotReady[.mic] ?? 0
        let sysOF = droppedOverflow[.system] ?? 0
        let micOF = droppedOverflow[.mic] ?? 0
        let sysStop = droppedAtStop[.system] ?? 0
        let micStop = droppedAtStop[.mic] ?? 0
        let sysPend = pending[.system]?.count ?? 0
        let micPend = pending[.mic]?.count ?? 0
        fputs(
            "DIAG: drops_not_ready system=\(sysNR) mic=\(micNR) "
                + "drops_overflow system=\(sysOF) mic=\(micOF) "
                + "drops_at_stop system=\(sysStop) mic=\(micStop) "
                + "pending_at_stop system=\(sysPend) mic=\(micPend)\n",
            stderr
        )
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
