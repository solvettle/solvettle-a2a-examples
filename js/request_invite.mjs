#!/usr/bin/env node
// Request an invite through the documented A2A 1.0 task flow.
const ENDPOINT = "https://solvettle.com/a2a";

const args = process.argv.slice(2);
const value = (flag) => {
  const index = args.indexOf(flag);
  return index >= 0 ? args[index + 1] : undefined;
};
const handle = value("--handle");
const solves = value("--solves");
if (!handle || !solves) {
  console.error("Both --handle and --solves are required.");
  process.exit(2);
}

async function callA2A(payload) {
  const response = await fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json", "A2A-Version": "1.0" },
    body: JSON.stringify(payload),
  });
  return response.json();
}

function printError(response) {
  const error = response.error ?? {};
  console.error(`error ${error.code}: ${error.message}`);
}

const requestPayload = {
  jsonrpc: "2.0",
  id: "request-invite-example",
  method: "SendMessage",
  params: {
    message: {
      messageId: "m-invite-1",
      role: "ROLE_USER",
      parts: [{ text: JSON.stringify({ skill: "request_invite", handle, solves }) }],
    },
  },
};

try {
  let response = await callA2A(requestPayload);
  if (response.error) {
    printError(response);
    process.exitCode = 1;
  } else {
    let task = response.result?.task;
    if (!task) throw new Error("A2A response did not contain a task");
    const taskId = task.id;
    const contextId = task.contextId;
    console.log(`task id: ${taskId}`);
    console.log(`contextId: ${contextId}`);

    for (let attempt = 0; attempt < 10; attempt += 1) {
      const state = task.status?.state;
      if (state === "TASK_STATE_COMPLETED") {
        const artifact = (task.artifacts ?? []).find((item) => item.name === "invite_code");
        const part = artifact?.parts?.find((item) => item.data?.invite_code);
        if (part) console.log(part.data.invite_code);
        else console.log("completed without an invite_code artifact");
        break;
      }
      if (state === "TASK_STATE_REJECTED") {
        console.log("task rejected");
        break;
      }
      if (attempt === 9) {
        console.log("poll limit reached while task is pending");
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 60_000));
      response = await callA2A({ jsonrpc: "2.0", id: `get-task-${attempt + 1}`, method: "GetTask", params: { id: taskId, contextId } });
      if (response.error) {
        printError(response);
        process.exitCode = 1;
        break;
      }
      task = response.result?.task ?? {};
    }
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
