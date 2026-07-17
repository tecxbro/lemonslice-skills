---
name: lemonslice-appearance-rendering
description: Select LemonSlice model and aspect ratio, improve avatar source images, support non-human characters, and implement GPU WebGL green-screen compositing. Route runtime appearance changes to lemonslice-control-actions.
license: MIT
---

# LemonSlice appearance and rendering

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

## Model and aspect-ratio selection

Treat LiveKit Python, LiveKit Node, Pipecat, raw REST, and account access as separate surfaces. Use [`references/model-surface-matrix.md`](references/model-surface-matrix.md) and inspect installed signatures before editing.

- **Default/flagship:** general baseline when no verified model override is required.
- **Lite:** lower-resource option where the selected surface and account support it.
- **Flash:** latency-sensitive option; test the actual character for visual artifacts and motion quality.
- **Pro:** high-resolution/immersive use only after account and installed-SDK verification.

Choose a documented aspect ratio that fits the product layout. Preserve the source and output aspect ratio rather than stretching a mismatched stream. Re-check model-specific constraints instead of hard-coding them across every surface.

## Source image

Follow [`references/avatar-image-tips.md`](references/avatar-image-tips.md). The current raw self-managed API recommends 368×560 and may center-crop mismatched inputs. Keep important facial and body details inside a conservative safe area and test the actual selected model/layout.

## Green screen

Use green-screen compositing for:

- landscape experiences;
- floating avatars;
- custom environments;
- product UI overlays;
- backgrounds that should remain controlled by the client.

Use a solid lime-green source background and sample the **actual source-image green**. Implement chroma key in a WebGL fragment shader, not a CPU per-pixel canvas loop.

Tune similarity/threshold, smoothness, spill removal, edge feathering, and source-to-output scaling.

Implementation requirements:

- preserve aspect ratio;
- avoid CPU readback such as `getImageData()` on every frame;
- keep the WebRTC video track as the source texture;
- stop the render loop when the call ends or component unmounts;
- release WebGL textures, framebuffers, programs, canvases, and video references;
- respect device-pixel ratio without rendering unnecessarily large buffers;
- respond to resize/layout changes without stretching;
- provide a non-composited fallback when WebGL is unavailable or context creation fails.

Test frame rate, GPU use, edge quality, hair/fur, fast motion, green spill, Safari/Chrome behavior, and cleanup after repeated calls.

Runtime image changes belong to `lemonslice-control-actions` and are asynchronous; do not confuse source-image selection with a completed runtime replacement.

References:
- [`references/model-surface-matrix.md`](references/model-surface-matrix.md)
- [`references/avatar-image-tips.md`](references/avatar-image-tips.md)
- [`references/green-screen.md`](references/green-screen.md)
- https://lemonslice.com/docs/reference/green-screen.md
