# Scenario: Recording permissions

## Goal

Recording requests the correct macOS permissions and fails/guides clearly when they are missing; after grant, restart may be required.

## Preconditions

- macOS arm64
- Ability to revoke/grant Microphone and Screen & System Audio Recording in System Settings

## Flow

1. With permissions denied, click **Record**; note messaging.
2. Grant Microphone + Screen & System Audio Recording.
3. **Quit and relaunch** Scribe (typical after Screen Recording grant).
4. Record again; confirm capture works.

## Expected behavior

- Permission family matches ScreenCaptureKit + mic — not a claim that screen **video** is saved.
- Dist Info.plist usage strings remain accurate if packaging is involved.
- After proper grant + restart, Record produces a usable WAV for transcription.

## Edge cases

- Mic granted but Screen Recording denied → system audio missing or error; messaging should not claim full success.
- Permissions granted without restart → may still fail until relaunch; UX should mention restart when relevant.

## Related docs / tests

- [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md) macOS permissions
- [TESTING.md](../../TESTING.md) § E, [recording-to-transcript.md](./recording-to-transcript.md)
