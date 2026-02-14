// InsightPulse Docs AI - Embed Script
// Drop this script on any page to add the AI assistant widget

(function () {
  // Configuration from data attributes or defaults
  const script = document.currentScript as HTMLScriptElement;
  const config = {
    apiUrl: script?.dataset.apiUrl || "",
    tenantId: script?.dataset.tenantId || "",
    surface: script?.dataset.surface || "docs",
    position: (script?.dataset.position as "bottom-right" | "bottom-left") || "bottom-right",
    primaryColor: script?.dataset.primaryColor || "#2563eb",
    title: script?.dataset.title || "Ask AI",
    welcomeMessage: script?.dataset.welcomeMessage || "Hi! How can I help you today?",
  };

  if (!config.apiUrl || !config.tenantId) {
    console.error("DocsAI: Missing required data-api-url or data-tenant-id attributes");
    return;
  }

  // Create container
  const container = document.createElement("div");
  container.id = "insightpulse-docs-ai-container";
  document.body.appendChild(container);

  // State
  let isOpen = false;
  let messages: Array<{ role: string; content: string; citations?: any[] }> = [];

  // Styles
  const styles = document.createElement("style");
  styles.textContent = `
    #insightpulse-docs-ai-container {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 14px;
      line-height: 1.5;
    }
    #insightpulse-docs-ai-container * {
      box-sizing: border-box;
    }
    @keyframes docsai-pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    .docsai-thinking {
      animation: docsai-pulse 1.5s infinite;
    }
  `;
  document.head.appendChild(styles);

  // Render function
  function render() {
    const positionStyle = config.position === "bottom-left"
      ? "left: 20px; right: auto;"
      : "right: 20px; left: auto;";

    if (!isOpen) {
      container.innerHTML = `
        <button
          id="docsai-toggle-btn"
          style="
            position: fixed;
            bottom: 20px;
            ${positionStyle}
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background-color: ${config.primaryColor};
            color: #fff;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            transition: transform 0.2s, box-shadow 0.2s;
          "
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </button>
      `;

      document.getElementById("docsai-toggle-btn")?.addEventListener("click", () => {
        isOpen = true;
        if (messages.length === 0) {
          messages.push({ role: "assistant", content: config.welcomeMessage });
        }
        render();
      });
      return;
    }

    const messagesHtml = messages
      .map(
        (m) => `
        <div style="
          align-self: ${m.role === "user" ? "flex-end" : "flex-start"};
          max-width: 85%;
        ">
          <div style="
            padding: 10px 14px;
            border-radius: 12px;
            background-color: ${m.role === "user" ? config.primaryColor : "#f3f4f6"};
            color: ${m.role === "user" ? "#fff" : "#111"};
            white-space: pre-wrap;
          ">${escapeHtml(m.content)}</div>
          ${
            m.citations && m.citations.length > 0
              ? `
            <div style="margin-top: 8px; font-size: 11px; color: #6b7280;">
              Sources: ${m.citations
                .slice(0, 3)
                .map(
                  (c: any) =>
                    `<a href="${c.url || "#"}" target="_blank" style="color: ${config.primaryColor}; text-decoration: none; margin-right: 8px;">${escapeHtml(c.title || "Link")}</a>`
                )
                .join("")}
            </div>
          `
              : ""
          }
        </div>
      `
      )
      .join("");

    container.innerHTML = `
      <div style="
        position: fixed;
        bottom: 20px;
        ${positionStyle}
        width: 380px;
        height: 520px;
        display: flex;
        flex-direction: column;
        border-radius: 16px;
        border: 1px solid rgba(0,0,0,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.16);
        overflow: hidden;
        background-color: #ffffff;
        z-index: 9999;
      ">
        <!-- Header -->
        <div style="
          padding: 14px 16px;
          background-color: ${config.primaryColor};
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: space-between;
        ">
          <div style="display: flex; align-items: center; gap: 8px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <span style="font-weight: 600;">${config.title}</span>
          </div>
          <button id="docsai-close-btn" style="
            background: none;
            border: none;
            color: #fff;
            cursor: pointer;
            padding: 4px;
          ">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- Messages -->
        <div id="docsai-messages" style="
          flex: 1;
          padding: 12px 16px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 12px;
        ">
          ${messagesHtml}
          <div id="docsai-loading" style="display: none; align-self: flex-start;">
            <div style="padding: 10px 14px; border-radius: 12px; background-color: #f3f4f6; color: #6b7280;" class="docsai-thinking">
              Thinking...
            </div>
          </div>
        </div>

        <!-- Input -->
        <form id="docsai-form" style="
          padding: 12px 16px;
          border-top: 1px solid rgba(0,0,0,0.08);
          display: flex;
          gap: 8px;
        ">
          <input
            type="text"
            id="docsai-input"
            placeholder="Ask a question..."
            style="
              flex: 1;
              border-radius: 8px;
              border: 1px solid rgba(0,0,0,0.16);
              padding: 10px 12px;
              font-size: 14px;
              outline: none;
            "
          />
          <button type="submit" style="
            border-radius: 8px;
            border: none;
            padding: 10px 16px;
            font-size: 14px;
            font-weight: 500;
            background-color: ${config.primaryColor};
            color: #fff;
            cursor: pointer;
          ">
            Send
          </button>
        </form>
      </div>
    `;

    // Event listeners
    document.getElementById("docsai-close-btn")?.addEventListener("click", () => {
      isOpen = false;
      render();
    });

    document.getElementById("docsai-form")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.getElementById("docsai-input") as HTMLInputElement;
      const question = input.value.trim();
      if (!question) return;

      messages.push({ role: "user", content: question });
      input.value = "";
      render();

      const loadingEl = document.getElementById("docsai-loading");
      if (loadingEl) loadingEl.style.display = "block";

      try {
        const res = await fetch(config.apiUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question,
            tenantId: config.tenantId,
            surface: config.surface,
            context: {
              url: window.location.href,
              path: window.location.pathname,
            },
          }),
        });

        const data = await res.json();
        messages.push({
          role: "assistant",
          content: data.answer || "Sorry, I couldn't generate an answer.",
          citations: data.citations,
        });
      } catch (err) {
        messages.push({
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        });
      }

      render();
      const messagesEl = document.getElementById("docsai-messages");
      if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
    });
  }

  function escapeHtml(text: string): string {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Initial render
  render();
})();
