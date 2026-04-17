export function renderRelayPrompt(args: {
  role: string;
  goal: string;
  constraints: string;
  context: unknown;
  selected_primary_agent: string;
  support_agents: string[];
  agent_prompt_md?: string | null;
}) {
  const ctx =
    typeof args.context === "string"
      ? args.context
      : args.context == null
        ? ""
        : JSON.stringify(args.context, null, 2);

  const support = args.support_agents.length
    ? `\n[SUPPORT AGENTS]\n- ${args.support_agents.join("\n- ")}\n`
    : "";

  const agentPrompt =
    args.agent_prompt_md && args.agent_prompt_md.trim().length
      ? `\n[AGENT PROMPT]\n${args.agent_prompt_md.trim()}\n`
      : "";

  return [
    `[ROLE] ${args.role}`,
    `[GOAL] ${args.goal}`,
    `[CONSTRAINTS] ${args.constraints}`,
    `[ROUTING] primary_agent=${args.selected_primary_agent}`,
    support.trimEnd(),
    ctx ? `[CONTEXT]\n${ctx}` : `[CONTEXT]\n`,
    agentPrompt.trimEnd(),
    `[OUTPUT FORMAT]
1) Brief execution plan (3–5 bullets)
2) Apply commands
3) Test commands
4) Deploy/migration commands
5) Validation commands
6) Rollback strategy`,
  ]
    .filter(Boolean)
    .join("\n\n")
    .replace(/\n{3,}/g, "\n\n");
}
