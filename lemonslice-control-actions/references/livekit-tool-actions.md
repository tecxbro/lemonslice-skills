# LiveKit Tool Actions

## Contents
- Tool-call action pattern
- Action allowlist
- Readiness
- Startup action pattern
- Common mistakes

## Pattern
Use LLM tool calls when the action should be triggered by conversational context.

Example pattern:

```python
from livekit.agents import Agent, function_tool

class Assistant(Agent):
    @function_tool()
    async def celebrate(self) -> str:
        """Call this function when the user shares positive news."""
        return await self.trigger_action("celebrate")
```

Rules:

* Keep the tool name semantically clear.
* Use the tool docstring to tell the LLM when to call it.
* Map the tool to a supported internal action name.
* Keep the actual LemonSlice control call server-side.
* Do not expose LemonSlice API keys to the frontend.
* Do not let the LLM pass arbitrary raw action names directly to LemonSlice.

Rules:
- Keep API keys server-side.
- Map LLM tool names to supported internal action names.
- Do not let LLM send arbitrary action names to LemonSlice.
- Wait for `bot_ready`.
