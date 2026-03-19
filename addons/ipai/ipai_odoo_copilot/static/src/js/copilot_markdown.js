/** @odoo-module */

/**
 * Lightweight markdown renderer for Copilot chat bubbles.
 *
 * Supports: headings, bold, italic, inline code, code blocks,
 * unordered/ordered lists, links, and line breaks.
 *
 * Does NOT support: images, tables, nested lists, HTML passthrough.
 * This is intentionally minimal — no external dependency.
 */

/**
 * Escape HTML entities to prevent XSS.
 * @param {string} text
 * @returns {string}
 */
function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

/**
 * Render inline markdown (bold, italic, code, links).
 * @param {string} text — already HTML-escaped
 * @returns {string}
 */
function renderInline(text) {
    return text
        // inline code (must come before bold/italic to avoid conflicts)
        .replace(/`([^`]+)`/g, '<code class="o_ipai_copilot_code_inline">$1</code>')
        // bold
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        // italic
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        // links [text](url) — url is already escaped
        .replace(
            /\[([^\]]+)\]\(([^)]+)\)/g,
            '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
        );
}

/**
 * Render markdown text to safe HTML.
 * @param {string} raw — raw markdown string
 * @returns {string} — safe HTML
 */
export function renderMarkdown(raw) {
    if (!raw) return "";

    const lines = raw.split("\n");
    const result = [];
    let inCodeBlock = false;
    let codeBlockLines = [];
    let codeBlockLang = "";

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Code block toggle
        if (line.trimStart().startsWith("```")) {
            if (!inCodeBlock) {
                inCodeBlock = true;
                codeBlockLang = line.trimStart().slice(3).trim();
                codeBlockLines = [];
            } else {
                inCodeBlock = false;
                const code = escapeHtml(codeBlockLines.join("\n"));
                const langAttr = codeBlockLang
                    ? ` data-language="${escapeHtml(codeBlockLang)}"`
                    : "";
                result.push(
                    `<pre class="o_ipai_copilot_code_block"${langAttr}><code>${code}</code></pre>`
                );
            }
            continue;
        }

        if (inCodeBlock) {
            codeBlockLines.push(line);
            continue;
        }

        const trimmed = line.trim();

        // Empty line → paragraph break
        if (!trimmed) {
            result.push("<br/>");
            continue;
        }

        // Headings
        const headingMatch = trimmed.match(/^(#{1,4})\s+(.+)/);
        if (headingMatch) {
            const level = headingMatch[1].length;
            const text = renderInline(escapeHtml(headingMatch[2]));
            result.push(
                `<div class="o_ipai_copilot_heading o_ipai_copilot_h${level}">${text}</div>`
            );
            continue;
        }

        // Unordered list
        if (/^[-*]\s+/.test(trimmed)) {
            const text = renderInline(escapeHtml(trimmed.replace(/^[-*]\s+/, "")));
            result.push(
                `<div class="o_ipai_copilot_list_item">• ${text}</div>`
            );
            continue;
        }

        // Ordered list
        const olMatch = trimmed.match(/^(\d+)[.)]\s+(.+)/);
        if (olMatch) {
            const text = renderInline(escapeHtml(olMatch[2]));
            result.push(
                `<div class="o_ipai_copilot_list_item">${escapeHtml(olMatch[1])}. ${text}</div>`
            );
            continue;
        }

        // Regular paragraph
        result.push(
            `<div class="o_ipai_copilot_paragraph">${renderInline(escapeHtml(trimmed))}</div>`
        );
    }

    // Handle unclosed code block
    if (inCodeBlock && codeBlockLines.length) {
        const code = escapeHtml(codeBlockLines.join("\n"));
        result.push(
            `<pre class="o_ipai_copilot_code_block"><code>${code}</code></pre>`
        );
    }

    return result.join("");
}
