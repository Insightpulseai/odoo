export function normalizeMarkdown(input) {
  let s = input ?? "";

  // Normalize line endings + trim trailing whitespace
  s = s.replace(/\r\n/g, "\n").replace(/[ \t]+$/gm, "");

  // Collapse >2 blank lines into 2
  s = s.replace(/\n{3,}/g, "\n\n");

  // Normalize headings: ensure a blank line before headings
  s = s.replace(/([^\n])\n(#{1,6}\s)/g, "$1\n\n$2");

  // Normalize lists indentation (common Turndown noise)
  s = s.replace(/^\s{2,}(-|\*|\d+\.)\s/gm, "$1 ");

  // Normalize fenced code blocks (ensure blank lines around)
  s = s.replace(/([^\n])\n```/g, "$1\n\n```");
  s = s.replace(/```\n([^\n])/g, "```\n$1");

  // Ensure file ends with single newline
  s = s.replace(/\n*$/, "\n");

  return s;
}
