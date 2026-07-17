import { voice } from "@livekit/agents";
import * as lemonslice from "@livekit/agents-plugin-lemonslice";

// Installed package types only expose agentImageUrl and agentId.
const avatar = new lemonslice.AvatarSession({ agentImageUrl: "https://example.com/current.png" });
export const session = new voice.AgentSession({});
