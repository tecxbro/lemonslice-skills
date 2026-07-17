from livekit import agents
from livekit.agents import AgentSession

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    session = AgentSession()
    await session.start(room=ctx.room)
