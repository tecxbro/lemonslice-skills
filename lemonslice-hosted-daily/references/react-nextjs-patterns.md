# React and Next.js Patterns

## Contents
- Client/server boundary
- Recommended modules
- Daily client setup
- Hook responsibilities
- App Router guidance
- Forbidden frontend code

## Client/server boundary
- Daily UI must be client-side.
- Hosted room creation must be server-side.
- Do not put `LEMONSLICE_API_KEY` in `NEXT_PUBLIC_*`.
- Do not call Lemon Slice REST APIs from client components.

## Guidance
For Next.js App Router:

- Put Daily room UI in a client component.
- Use `"use client"` for components that use Daily, browser media APIs, or React hooks tied to the call object.
- Keep hosted room creation in a server route, route handler, server action, or external backend.
- Do not place `LEMONSLICE_API_KEY` in public env vars such as `NEXT_PUBLIC_*`.
- Do not call LemonSlice directly from client components.

Recommended frontend modules:

- `HostedDailyRoom.tsx`: client component for Daily room UI
- `useHostedDailySession.ts`: hook that owns state machine, join, event handlers, cleanup
- `app/api/.../route.ts` or backend route: creates hosted room through `lemonslice-hosted`

Recommended hook responsibilities:

- store current state
- request credentials from backend
- create Daily call object
- join Daily
- register event listeners (memoize event callbacks when using Daily React hooks)
- start/clear startup timeout
- send app messages
- leave/destroy on cleanup
