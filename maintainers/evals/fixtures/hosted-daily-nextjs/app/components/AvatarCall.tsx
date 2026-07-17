"use client";

export function AvatarCall() {
  async function start() {
    await fetch("https://lemonslice.com/api/liveai/rooms", {
      headers: { "X-API-Key": process.env.NEXT_PUBLIC_LEMONSLICE_API_KEY! },
    });
  }
  return <button onClick={start}>Start</button>;
}
