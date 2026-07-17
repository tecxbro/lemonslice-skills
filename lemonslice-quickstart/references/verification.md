# Quickstart verification

Complete all applicable checks before reporting the project finished.

## Repository

- The official starter structure is integrated into the real application entrypoints.
- The existing package manager and lockfile are preserved.
- No second agent architecture was added beside an existing LiveKit app.
- `LEMONSLICE_API_KEY` appears only in trusted server/agent configuration.

## Agent

- The LiveKit worker starts without import or constructor errors.
- The installed LemonSlice plugin accepts every configured option.
- Existing STT, VAD/turn detection, LLM, TTS, tools, and conversation state are preserved unless intentionally changed.
- Startup failure, idle timeout, disconnect, and process-shutdown paths terminate resources.

## Browser

- The browser receives scoped LiveKit credentials from trusted code.
- The room connection succeeds.
- The expected LemonSlice avatar participant and remote video track are identified.
- Pipeline readiness and first rendered frame are separate gates.
- The active-call UI begins only after a real avatar frame renders.

## Commands

Run the repository's install, formatter, type checker, tests, and production build. Record the exact commands and results; never claim an unrun command passed.
