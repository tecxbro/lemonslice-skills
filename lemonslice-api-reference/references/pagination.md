# Pagination

List endpoints use `page` and `limit` query parameters.

- Validate both values as positive integers.
- Cap `limit` at 100.
- Preserve returned pagination metadata, including `has_more`.
- Do not infer completion from a short page when the response explicitly provides `has_more`.
- Keep pagination independent for `/liveai/sessions` and `/liveai/rooms`.
- Stop on malformed metadata rather than looping indefinitely.

Treat exact field names and defaults as OpenAPI-owned and re-check them when the snapshot changes.
