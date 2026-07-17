# Avatar image tips

## API recommendation

- The current raw self-managed API recommends a **368×560** source image.
- Inputs that do not match the target dimensions may be center-cropped.
- Keep the important face, mouth, hands, clothing, and props away from crop-sensitive edges.
- Do not stretch an image to force the desired aspect ratio.
- Test the final image using the actual selected model and layout.

## Close-up conversational avatars

- Keep the face and mouth large, clear, and evenly lit.
- Leave modest headroom while avoiding large empty margins.
- Keep hair and chin inside the likely center crop.
- Prefer simple backgrounds that do not compete with facial motion.

## Waist-up hand-gesture avatars

- Include shoulders, elbows, and expected gesture space.
- Keep hands away from the extreme sides and bottom edge.
- Use clothing with a readable silhouette and avoid crop-sensitive props.
- Test motion at the final UI aspect ratio rather than judging the still image alone.

## Full-body characters

- Leave enough floor and overhead space for motion without making the face too small.
- Keep feet, hands, and held objects inside a conservative safe area.
- Confirm that the selected model, account, and integration support the intended full-body behavior.

## Cartoon and non-human characters

- Preserve recognizable eyes, mouth, and a face-like structure.
- Use clear edges and sufficient contrast between the character and background.
- Test unusual proportions, snouts, beaks, masks, or mascot heads with real speech and motion.

## Green-screen sources

- Use a consistent lime-green background with even lighting.
- Avoid green clothing, props, reflections, and semi-transparent green details.
- Keep hair, fur, motion blur, and fine edges away from strong green spill.
- Sample the actual source-image green in the compositor and provide a non-composited fallback.
