---
name: lemonslice-widget
description: Embeds and controls the no-backend Lemon Slice web widget. Use for HTML, Next.js, Shopify, Squarespace, Wix, widget customization, widget methods, and backend/admin call metadata.
license: MIT
---

# Lemon Slice Widget Integration

## Use this skill when
- Router selected Widget.
- User wants a no-backend website embed.
- User is using HTML, Next.js, Shopify, Squarespace, or Wix.
- User needs the prebuilt Lemon Slice web component.
- User needs widget attributes, widget methods, or widget call metadata.

## Do not use this skill when
- Project uses LiveKit → `lemonslice-livekit`
- Project uses Pipecat → `lemonslice-pipecat`
- Developer owns STT/LLM/TTS and needs raw session control → `lemonslice-self-managed`
- LemonSlice manages STT/LLM/TTS but developer wants custom Daily frontend → `lemonslice-hosted` + `lemonslice-hosted-daily`
- Task is raw REST/API debugging → `lemonslice-api-reference`
- Task is session/action/emotion control outside Widget API → `lemonslice-control-actions`
- Implementation would expose `X-API-Key` in browser code

## Basic embed
```html
<lemon-slice-widget agent-id="AGENT_ID_HERE"></lemon-slice-widget>
<script type="module" src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"></script>
```

## Core rules
- `agent-id` is required.
- Script loads once.
- Do not expose API keys.
- Do not duplicate script/widget unless intentional.
- Widget controls are element methods, not self-managed REST controls.
- Widget metadata uses `/api/liveai/rooms`, backend/admin only.

## Reference files
Load only the reference file needed for the widget task:

- `references/embed-guides.md` — read for HTML, Next.js, Shopify, Squarespace, or Wix placement details.
- `references/customization-controls-metadata.md` — read for widget attributes, widget methods, and backend/admin call metadata.

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
