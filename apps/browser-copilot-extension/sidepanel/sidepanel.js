const chat = document.getElementById("chat");
const cmd = document.getElementById("cmd");
const send = document.getElementById("send");

function addMessage(text, cls) {
  const div = document.createElement("div");
  div.className = `msg ${cls}`;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function addCapture(captureId, captureType) {
  const div = document.createElement("div");
  div.className = "msg capture";
  div.innerHTML = `<span class="capture-icon">📸</span> Captured: ${captureType} (${captureId})`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function handleCommand() {
  const text = cmd.value.trim();
  if (!text) return;

  addMessage(text, "user");
  cmd.value = "";

  try {
    const response = await chrome.runtime.sendMessage({
      type: "agent.command",
      text: text,
      timestamp: new Date().toISOString(),
    });

    if (response?.type === "capture.complete") {
      addCapture(response.captureId, response.captureType);
    } else if (response?.type === "capture.error") {
      addMessage(`Error: ${response.error}`, "system");
    } else {
      addMessage(`Unrecognized: "${text}"`, "system");
    }
  } catch (err) {
    addMessage(`Error: ${err}`, "system");
  }
}

send.addEventListener("click", handleCommand);
cmd.addEventListener("keydown", (e) => {
  if (e.key === "Enter") handleCommand();
});

// Listen for capture notifications from background
chrome.runtime.onMessage.addListener((msg) => {
  if (msg?.type === "capture.complete") {
    addCapture(msg.captureId, msg.captureType);
  }
});

addMessage("Ready. Type 'ss' to capture active window.", "system");
