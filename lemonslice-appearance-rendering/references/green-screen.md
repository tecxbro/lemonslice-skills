# WebGL green-screen guidance

1. Use a solid lime-green reference background.
2. Sample its exact RGB/hex value.
3. Upload each WebRTC frame as a WebGL texture.
4. In a fragment shader, compute color distance from the key color.
5. Convert distance to alpha using similarity and smoothness thresholds.
6. Reduce green spill and feather edges.
7. Composite over a background texture/CSS layer.
8. Avoid CPU `getImageData`/per-pixel loops in the render path.
9. Measure frame rate, main-thread time, GPU load, and edge quality.
