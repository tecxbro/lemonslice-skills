---
name: lemonslice-widget
description: Embed and control the no-backend LemonSlice web widget. Use this when the user wants a fast website embed for HTML, Next.js, Shopify, Squarespace, Wix, marketing sites, demos, or evaluation using `<lemon-slice-widget>` and the hosted widget script. Covers `agent-id`, script placement, customization attributes, widget methods like `micOn`, `mute`, `sendMessage`, and backend-only metadata calls. Do not use for LiveKit, Pipecat, Self-Managed REST, Hosted Daily custom frontend, or any flow exposing `X-API-Key` in browser code.
license: MIT
---

# Lemon Slice Widget Integration

## Official docs

- https://lemonslice.com/docs/widget/overview.md
- https://lemonslice.com/docs/widget/customization.md
- https://lemonslice.com/docs/widget/control.md
- https://lemonslice.com/docs/widget/call-metadata.md
- https://lemonslice.com/docs/widget/prompt-engineering.md
- https://lemonslice.com/docs/widget/embed-guides/nextjs.md
- https://lemonslice.com/docs/widget/embed-guides/shopify.md
- https://lemonslice.com/docs/widget/embed-guides/squarespace.md
- https://lemonslice.com/docs/widget/embed-guides/wix.md

## Use this skill when

This skill is for:
* no-backend website embeds
* basic HTML sites
* marketing websites
* demos/evaluation
* Shopify stores
* Squarespace sites
* Wix sites
* Next.js apps using the prebuilt widget
* frontend agents adding the LemonSlice web component

> **Guardrail:** Use only after `lemonslice-integration-choice` has explicitly selected this path.

## Do not use this skill when

Do not use Widget when:
* project uses LiveKit → use `lemonslice-livekit`
* project uses Pipecat → use `lemonslice-pipecat`
* developer owns STT/LLM/TTS and needs raw session control → use `lemonslice-self-managed`
* LemonSlice manages STT/LLM/TTS but developer wants custom Daily frontend → use `lemonslice-hosted` + `lemonslice-hosted-daily`
* task is raw REST/API debugging → use `lemonslice-api-reference`
* task is session/action/emotion control outside Widget API → use `lemonslice-control-actions`
* user wants full custom UI/media/session lifecycle
* implementation would expose `X-API-Key` in browser code

## Basic HTML embed

```html
<lemon-slice-widget agent-id="AGENT_ID_HERE"></lemon-slice-widget>
<script type="module" src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"></script>
```

The LemonSlice agent must already exist in the LemonSlice web app. Platform embed guides assume the agent is available on the required LemonSlice plan.

* replace `AGENT_ID_HERE`
* `agent-id` is required
* script should be loaded once
* place near end of `<body>` for plain HTML
* do not expose API keys
* do not duplicate script/widget unless intentional

## Next.js guide

For App Router:
* put widget in `app/layout.tsx`
* place inside `<body>` after `{children}`
* load script once
* do not put on every page
* add TypeScript custom-element declaration if needed

For production Next.js apps, prefer `next/script` if the app’s lint or runtime rules discourage raw `<script>` tags in layouts.

```tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <lemon-slice-widget agent-id="AGENT_ID_HERE" />
        <script
          type="module"
          src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"
        />
      </body>
    </html>
  );
}
```

```ts
declare global {
  namespace JSX {
    interface IntrinsicElements {
      "lemon-slice-widget": {
        "agent-id": string;
        "initial-state"?: "minimized" | "active" | "hidden";
        "controlled-widget-state"?: "minimized" | "active" | "hidden";
        "custom-active-width"?: string;
        "custom-active-height"?: string;
        "custom-minimized-width"?: string;
        "custom-minimized-height"?: string;
        inline?: boolean;
        "hide-ui"?: boolean;
        "controlled-show-minimize-button"?: "true" | "false";
        "show-minimize-button"?: "true" | "false";
        "video-button-color-hex"?: string;
        "video-button-color-opacity"?: string;
      };
    }
  }
}

export {};
```

## Shopify guide

Shopify admin → Online Store → Themes → active theme → Edit code → layout/theme.liquid

Add the embed inside the `<body>` tag in `layout/theme.liquid`, before the first existing `<script>` tag.

```liquid
<lemon-slice-widget agent-id="AGENT_ID_HERE"></lemon-slice-widget>
<script type="module" src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"></script>
```

* do not paste in multiple snippets
* do not expose API keys
* use `theme.liquid` for site-wide widget
* use page/product template only if intentionally page-specific

## Squarespace guide

* use Code Injection
* site-wide injection for whole site
* page-level injection for one page
* Use Page Settings → Advanced → Page header code injection for the page-level embed. Verify on the live site because the widget may not display in editor preview.
* do not inject duplicate script
* do not expose API keys

```html
<lemon-slice-widget agent-id="AGENT_ID_HERE"></lemon-slice-widget>
<script type="module" src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"></script>
```

## Wix guide

Wix Dashboard → Settings → Custom Code / Advanced Custom Code

* add the widget tag and script
* Recommended: select All pages and Load code once so the widget persists across pages. Avoid selecting only certain pages unless intentional, because the agent may restart when users navigate.
* publish the site
* verify live site
* avoid duplicate per-page embeds
* do not expose API keys

```html
<lemon-slice-widget agent-id="AGENT_ID_HERE"></lemon-slice-widget>
<script type="module" src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"></script>
```

## Customization attributes

| Attribute | Description |
|---|---|
| `agent-id` | Required. The ID of the agent. |
| `initial-state` | Set to "minimized", "active", or "hidden". |
| `controlled-widget-state` | Programmatic state control. |
| `custom-active-width` | Custom width when active. |
| `custom-active-height` | Custom height when active. |
| `custom-minimized-width` | Custom width when minimized. |
| `custom-minimized-height` | Custom height when minimized. |
| `inline` | Render inline rather than as overlay. |
| `hide-ui` | Hide the default widget UI elements. |
| `controlled-show-minimize-button` | Programmatically toggle the minimize button. |
| `show-minimize-button` | Toggle the minimize button visibility. |
| `video-button-color-hex` | Custom hex color for the video button. |
| `video-button-color-opacity` | Opacity of the custom video button color. |

Start active:

```html
<lemon-slice-widget
  agent-id="AGENT_ID_HERE"
  initial-state="active"
></lemon-slice-widget>
```

Custom color:

```html
<lemon-slice-widget
  agent-id="AGENT_ID_HERE"
  video-button-color-hex="#FF4FD8"
  video-button-color-opacity="0.8"
></lemon-slice-widget>
```

Inline:

```html
<lemon-slice-widget
  agent-id="AGENT_ID_HERE"
  inline
  initial-state="active"
></lemon-slice-widget>
```

## Programmatic controls

| Method | Description |
|---|---|
| `mute()` | Control output audio (mute). |
| `unmute()` | Control output audio (unmute). |
| `isMuted()` | Check if output audio is muted. |
| `canUnmute()` | Check if audio can be unmuted. |
| `micOn()` | Control microphone (turn on). |
| `micOff()` | Control microphone (turn off). |
| `isMicOn()` | Check if microphone is on. |
| `canTurnOnMic()` | Check if microphone can be turned on. |
| `sendMessage(message)` | Sends text message to agent. |

* `mute()` / `unmute()` control output audio
* `micOn()` / `micOff()` control microphone
* `sendMessage(message)` sends text to agent
* async methods should be awaited
* `micOn()` and `sendMessage()` can start/join the room if needed
* do not invent unsupported methods

```js
const widget = document.querySelector("lemon-slice-widget");

await widget.micOn();
await widget.sendMessage("Hello, agent!");
await widget.mute();

if (widget.isMuted()) {
  console.log("Audio is muted");
}
```

## Call metadata

Widget metadata uses Rooms API, not Self-Managed Sessions API.

```bash
curl -X GET "https://lemonslice.com/api/liveai/rooms?page=1&limit=25" \
  -H "X-API-Key: YOUR_API_KEY"
```

```bash
curl -X GET "https://lemonslice.com/api/liveai/rooms/SESSION_ID" \
  -H "X-API-Key: YOUR_API_KEY"
```

* metadata calls require `X-API-Key`
* do this from backend/admin tooling only
* never expose `X-API-Key` in browser code
* do not use `/liveai/sessions` for Widget metadata

For completed sessions, the response can include additional metadata such as credits used and transcript.

## Common mistakes

* using Widget when LiveKit/Pipecat is needed
* using Widget for custom Daily frontend
* exposing `X-API-Key` in browser code
* loading script multiple times
* mounting widget on every SPA route
* adding unsupported attributes
* calling unsupported methods
* using `/liveai/sessions` instead of `/liveai/rooms`
* forgetting `agent-id`
* assuming website-builder preview is enough; must check published/live site

## Validation checklist

- [ ] Router selected `lemonslice-widget`
- [ ] Target platform is clear: HTML, Next.js, Shopify, Squarespace, or Wix
- [ ] `agent-id` is present
- [ ] Script is loaded once
- [ ] Widget is mounted globally if persistence is needed
- [ ] Next.js uses `app/layout.tsx`
- [ ] Shopify uses `layout/theme.liquid` for site-wide install
- [ ] Squarespace/Wix live site is checked after publishing
- [ ] Attributes are documented
- [ ] Methods are documented
- [ ] Metadata uses `/api/liveai/rooms`
- [ ] `X-API-Key` is not exposed in frontend code
- [ ] LiveKit/Pipecat/Hosted Daily/Self-managed work is routed away from Widget
