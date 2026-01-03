/** @odoo-module **/
import { reactive } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

let _id = 0;
const uid = () => `${Date.now()}_${++_id}`;

export const copilotState = reactive({
  open: false,
  loading: false,
  draft: "",
  messages: [], // {id, role: 'user'|'assistant', text, citations?}
});

export function openCopilot() {
  copilotState.open = true;
}

export function closeCopilot() {
  copilotState.open = false;
}

export function newChat() {
  copilotState.messages = [];
  copilotState.draft = "";
}

export async function sendMessage(text, context = {}) {
  const trimmed = (text || "").trim();
  if (!trimmed) return;

  copilotState.messages.push({ id: uid(), role: "user", text: trimmed });
  copilotState.draft = "";
  copilotState.loading = true;

  try {
    const res = await rpc("/ipai/copilot/query", {
      message: trimmed,
      context,
    });

    if (!res || res.ok === false) {
      copilotState.messages.push({
        id: uid(),
        role: "assistant",
        text: res?.error || "Copilot error",
      });
      return;
    }

    const citations = (res.citations || []).map((c, idx) => ({
      key: `${idx}_${c.id || ""}`,
      title: c.title || c.source || c.section || "Source",
      url: c.url || c.link || "",
    }));

    copilotState.messages.push({
      id: uid(),
      role: "assistant",
      text: res.answer || "(no answer)",
      citations,
    });
  } catch (e) {
    copilotState.messages.push({
      id: uid(),
      role: "assistant",
      text: `Request failed: ${e?.message || e}`,
    });
  } finally {
    copilotState.loading = false;
  }
}
