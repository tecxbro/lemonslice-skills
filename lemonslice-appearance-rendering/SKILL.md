---
name: lemonslice-appearance-rendering
description: Select LemonSlice model and aspect ratio, improve avatar source images, support non-human/cartoon characters, and implement GPU WebGL green-screen compositing. Route runtime appearance changes to lemonslice-control-actions.
license: MIT
---

# LemonSlice appearance and rendering

Follow [`../references/implementation-contract.md`](../references/implementation-contract.md).

## Model selection

- **Standard/default:** general production baseline.
- **Lite:** lower resolution/cost for high-volume consumer use; current docs support only `2x3` and `1x1`.
- **Flash:** lower-latency option; test the actual character for visual artifacts and motion quality before production.
- **Pro:** high-resolution/immersive use when account access and installed SDK support are confirmed.

Inspect installed plugin signatures and account availability. Do not send model/aspect fields through raw REST unless the current schema supports them.

## Aspect ratio

Choose from documented `2x3`, `9x16`, and `1x1`, subject to model limits. Reject Lite + `9x16`. Match the product layout rather than stretching a mismatched stream.

## Source image

- clear face and mouth;
- tight, intentional framing;
- minimal dead space;
- adequate resolution and lighting;
- test anthropomorphic, stylized, cartoon, and non-human characters;
- for Lite, prefer stylized characters or tight photorealistic face crops.

## Green screen

Use a solid lime-green source background and sample the **actual source-image green**. Implement chroma key in a WebGL fragment shader, not a CPU per-pixel canvas loop.

Tune:

- similarity/threshold;
- smoothness;
- spill removal;
- edge feathering;
- source-to-output scaling.

Keep the WebRTC video track as the source texture and composite over the desired background. Test frame rate, GPU use, edges, hair, motion, and Safari/Chrome compatibility.

Runtime image changes belong to `lemonslice-control-actions`.

See references for model constraints, image tips, and shader guidance.
