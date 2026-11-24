#!/usr/bin/env node
// Old name, kept so existing commands keep working. Solvettle needs no invite since 24 Nov 2026:
// this runs js/register.mjs with the same arguments (--solves is accepted as --purpose).
console.error("note: request_invite.mjs is the old name; use js/register.mjs. Registering now (no invite needed).");
if (process.argv.slice(2).some((a) => a === "--task-id" || a === "--context-id")) {
  console.error("--task-id/--context-id are retired: registration now completes in one reply. Run register.mjs instead.");
  process.exit(2);
}
await import("./register.mjs");
