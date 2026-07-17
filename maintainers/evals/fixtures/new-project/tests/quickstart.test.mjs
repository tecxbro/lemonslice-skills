import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("agent entrypoint uses LemonSlice and a server-only key", async () => {
  const agent = await read("src/agent.ts");
  assert.match(agent, /AvatarSession/);
  assert.match(agent, /LEMONSLICE_API_KEY/);
  assert.doesNotMatch(agent, /NEXT_PUBLIC_LEMONSLICE_API_KEY/);
});

test("page imports the call component", async () => {
  const page = await read("app/page.tsx");
  assert.match(page, /AvatarCall/);
  assert.match(page, /from\s+["'][^"']*AvatarCall["']/);
});

test("active call UI waits for a first rendered frame", async () => {
  const component = await read("app/components/AvatarCall.tsx");
  assert.match(component, /frame/i);
  assert.match(component, /ready/i);
  assert.doesNotMatch(component, /bot_ready[^\n]*setActive\(true\)/);
});

test("browser files do not expose the server key", async () => {
  const page = await read("app/page.tsx");
  const component = await read("app/components/AvatarCall.tsx");
  assert.doesNotMatch(page + component, /LEMONSLICE_API_KEY|X-API-Key/);
});
