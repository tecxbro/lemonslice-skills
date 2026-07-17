---
name: lemonslice-widget
description: Embed and control the LemonSlice web component in static sites, React, or Next.js. Covers use criteria, customization routing, consent, safe lifecycle, metadata ownership, and SPA cleanup.
license: MIT
---

# LemonSlice Widget

## Use criteria

Use the Widget when:

- the user wants the fastest no-backend embed;
- LemonSlice owns the agent pipeline and call experience;
- deep application-owned lifecycle control is not required.

Use Hosted or Self-Managed instead when the application needs custom authorization, transport ownership, provider selection, detailed state reconciliation, or a deeply custom call UI.

## Customization routing

- visual configuration → widget customization reference;
- runtime methods/events → widget control reference;
- user/tenant call association → call metadata reference;
- Shopify, Wix, Squarespace, Next.js, or other platform work → platform embed reference;
- spoken behavior → prompt-engineering reference.

## Security and consent

Load the documented widget script once, render the custom element with the configured agent ID, and never expose `LEMONSLICE_API_KEY`.

Do not auto-start microphone capture merely because the element mounted. Preserve the site's explicit user-consent interaction and the browser's permission flow.

Do not treat microphone capability probes as authorization, consent, or reliable call state. Prefer documented events and handle method results defensively.

## React and Next.js lifecycle

Require:

- client-only initialization;
- the script loaded exactly once;
- no duplicate custom-element registration;
- no server rendering of `window`, `document`, `customElements`, media devices, or other browser-only APIs;
- teardown/end-call handling on route change and component unmount;
- removal of every event listener registered by the component;
- protection against effects running twice in development;
- no stale widget reference after navigation.

```tsx
const widgetRef = useRef<HTMLElement | null>(null);

useEffect(() => {
  let cancelled = false;
  const listeners: Array<() => void> = [];

  customElements.whenDefined("lemonslice-widget").then(() => {
    if (cancelled) return;
    // Register documented listeners here and store their removers.
  });

  return () => {
    cancelled = true;
    for (const remove of listeners) remove();
    // End/cleanup the active call when the documented API supports it.
    widgetRef.current = null;
  };
}, []);
```

## Prompt engineering

Prompts should optimize spoken behavior: use short sections, distinguish speech from UI behavior, repeat critical constraints where useful, normalize symbols/URLs/numbers for TTS, and test the actual voice output.

## Metadata and authorization

When backend calls attach metadata or associate calls with users/tenants:

- authenticate and authorize the app user;
- validate and allowlist metadata;
- store ownership in app records;
- never trust browser-supplied ownership claims;
- do not expose server credentials.

References:
- [`references/platform-embeds.md`](references/platform-embeds.md)
- [`references/prompt-engineering.md`](references/prompt-engineering.md)
- https://lemonslice.com/docs/widget/overview.md
- https://lemonslice.com/docs/widget/control.md
- https://lemonslice.com/docs/widget/prompt-engineering.md
