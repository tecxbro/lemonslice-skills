import { access, readFile } from "node:fs/promises";

const required = [
  "src/agent.ts",
  "app/page.tsx",
  "app/components/AvatarCall.tsx",
  ".env.example",
];

for (const path of required) {
  await access(path);
}

const page = await readFile("app/page.tsx", "utf8");
const component = await readFile("app/components/AvatarCall.tsx", "utf8");
const agent = await readFile("src/agent.ts", "utf8");
const env = await readFile(".env.example", "utf8");

if (!/from\s+["'][^"']*AvatarCall["']/.test(page)) {
  throw new Error("app/page.tsx must import AvatarCall");
}
if (!/AvatarSession/.test(agent)) {
  throw new Error("src/agent.ts must wire AvatarSession");
}
if (!/LEMONSLICE_API_KEY/.test(agent + env)) {
  throw new Error("server-only LemonSlice key declaration is missing");
}
if (/NEXT_PUBLIC_LEMONSLICE_API_KEY/.test(agent + page + component + env)) {
  throw new Error("LemonSlice API key must not be public");
}
if (!/frame/i.test(component) || !/ready/i.test(component)) {
  throw new Error("AvatarCall must model first-frame readiness");
}

console.log("Import graph and server/browser boundaries are valid.");
