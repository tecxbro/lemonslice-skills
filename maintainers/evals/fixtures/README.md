# Evaluation fixture tiers

## Routing fixtures

Small fixtures isolate routing decisions and refusal/no-op behavior. They are not treated as proof that a framework integration compiles.

## Implementation fixtures

Implementation fixtures contain meaningful imports, lifecycle assertions, server/browser credential boundaries, and validation commands. The `new-project` fixture is the first implementation-tier fixture: its tests fail before LemonSlice wiring and require the agent entrypoint, page-to-component import graph, server-only API key handling, and first-frame readiness behavior.

Behavioral command outcomes must be produced by an externally isolated executor. The scorer never runs project commands directly.
