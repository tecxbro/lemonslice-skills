# Widget Customization, Controls, and Metadata

## Contents
- Customization attributes
- Programmatic methods
- Call metadata
- Backend/admin API-key boundary
- Common mistakes

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

## Programmatic methods
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
