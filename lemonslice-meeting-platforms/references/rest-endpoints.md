# Meeting REST endpoints

## Join

`POST /liveai/sessions/{session_id}/join-meeting`

Requires `X-API-Key`. Body:

- `meeting_url` (Zoom, Google Meet, Microsoft Teams, or Webex)
- `livekit_url`
- `broadcast_token`
- optional `bot_name`

Response:

- `meeting_bot_id`
- `websocket_url` for the meeting audio tunnel

## Leave

Use the documented leave endpoint with the stored `meeting_bot_id`. Call it on every terminal path, including partial startup failure and deployment shutdown.
