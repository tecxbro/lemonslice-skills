# Control Dispatcher

## Contents
- Why a dispatcher is needed
- Required tracked state
- Rejection rules
- Queue/debounce policy
- Stale session protection
- Example type shape

## Track
- `isAvatarReady`
- `isTerminated`
- `actionInFlight`
- `imageUpdateInFlight`
- current session id
- terminal error state

## Reject controls when
- avatar not ready
- already terminated
- conflicting action in flight
- stale session id
- terminal error exists

```ts
type AvatarControlCommand =
  | { type: "terminate" }
  | { type: "triggerAction"; name: string }
  | { type: "updateImage"; imageUrl: string }
  | { type: "updateAgentPrompt"; agentPrompt: string }
  | { type: "updateIdlePrompt"; idlePrompt: string }

async function dispatchAvatarControl(command: AvatarControlCommand) {
  assertAvatarReady()
  assertNotTerminated()
  assertNoConflictingActionInFlight(command)
  // Send through the selected control surface.
}
```
