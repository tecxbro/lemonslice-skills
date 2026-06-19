---
name: lemonslice-widget
description: Embed and control the Lemon Slice widget.
license: MIT
---

# Lemon Slice Widget Integration

## Use this skill when
The developer wants the simplest integration path: dropping a prebuilt web component onto a website (like Webflow, Shopify, WordPress) with minimal custom coding.

## Do not use this skill when
- The developer needs deep customization of the UI (use `lemonslice-hosted` or `lemonslice-self-managed`).
- The developer is building a custom LiveKit or Pipecat integration.
- Programmatic control over the conversation pipeline is required.

## Agent workflow
1. **HTML Embed:**
   - Use the web component: `<lemon-slice-widget agent-id="YOUR_AGENT_ID"></lemon-slice-widget>`.
   - Include the script: `<script type="module" src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"></script>`.
2. **Next.js Integration:**
   - Use `next/script` with `strategy="afterInteractive"`.
   - Place the component in `layout.tsx` to ensure it persists across page navigation.
3. **Customization:**
   - Appearance and voice are primarily configured in the Lemon Slice web app dashboard.
   - The widget states handle transitions between minimized (welcome loop), active, and hidden automatically.
4. **Metadata:**
   - The widget abstracts session details. To retrieve detailed metadata (like costs or transcripts), the backend must query `GET /api/liveai/rooms/{session_id}`.

## Common mistakes
- Attempting to heavily modify the widget's internal UI using CSS. If deep custom styling is needed, use the Hosted Pipeline instead.
- Re-mounting the widget on every page load in a single-page application (SPA). It should sit at the root layout level.

## Validation checklist
- [ ] Is the web component tag correctly formatted with the `agent-id`?
- [ ] In React/Next.js, is the script loaded in a non-blocking way (`afterInteractive`)?
- [ ] Is the widget placed globally so it doesn't interrupt the conversation on navigation?
