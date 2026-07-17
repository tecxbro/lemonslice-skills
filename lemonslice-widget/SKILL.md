---
name: lemonslice-widget
description: Embed and control the LemonSlice web component in static sites, React, or Next.js. Covers safe lifecycle, method caveats, prompt engineering, metadata ownership, and SPA cleanup.
license: MIT
---

# LemonSlice Widget

Use the Widget for a prebuilt LemonSlice-managed experience. Do not add a self-managed/Hosted backend unless the user asks for app-owned metadata or authorization.

## Integration

Load the documented widget script once, render the custom element with the configured agent ID, and never expose `LEMONSLICE_API_KEY`.

In React/Next.js, wait for the custom element definition before calling methods:

```tsx
const widgetRef = useRef<HTMLElement | null>(null);

useEffect(() => {
  let cancelled = false;
  customElements.whenDefined("lemonslice-widget").then(() => {
    if (!cancelled) {
      // widgetRef.current?.startCall?.()
    }
  });
  return () => {
    cancelled = true;
    // End/cleanup the call on route unmount when supported.
  };
}, []);
```

Verify script deduplication, call teardown, and event-listener cleanup across SPA navigation.

## Control caveat

Current widget implementations may not make `isMicOn()` and `canTurnOnMic()` reliable state probes. Prefer documented widget events and treat method results defensively; do not build critical authorization or state machines around those probes alone.

## Prompt engineering

Prompts should optimize spoken behavior:

- write short, clear sections;
- instruct spoken behavior, not visual UI behavior;
- repeat critical constraints where needed;
- normalize symbols, URLs, numbers, abbreviations, and punctuation for TTS;
- test the actual voice output.

## Metadata and authorization

When backend calls attach metadata or associate calls with users/tenants:

- authenticate and authorize the app user;
- validate and allowlist metadata;
- store ownership in app records;
- never trust browser-supplied ownership claims;
- do not expose server credentials.

Platform-specific embed guides live in `references/platform-embeds.md`; prompt guidance lives in `references/prompt-engineering.md`.

References:
- https://lemonslice.com/docs/widget/overview.md
- https://lemonslice.com/docs/widget/control.md
- https://lemonslice.com/docs/widget/prompt-engineering.md
