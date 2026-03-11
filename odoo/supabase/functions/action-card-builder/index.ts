// Odoo Copilot — Action Card Builder Edge Function
// Builds Slack Block Kit or Teams Adaptive Card JSON for business actions

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const { action_type, record_name, amount, target_platform, actor_name } =
    await req.json();

  if (target_platform === "slack") {
    const blocks = buildSlackBlocks(action_type, record_name, amount, actor_name);
    return new Response(JSON.stringify({ blocks }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  if (target_platform === "teams") {
    const card = buildTeamsCard(action_type, record_name, amount, actor_name);
    return new Response(JSON.stringify({ card }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  return new Response(
    JSON.stringify({ error: "unsupported platform" }),
    { status: 400, headers: { "Content-Type": "application/json" } }
  );
});

function buildSlackBlocks(
  actionType: string,
  recordName: string,
  amount: string | number,
  actorName: string
) {
  return [
    {
      type: "header",
      text: { type: "plain_text", text: `Action Required: ${actionType}` },
    },
    {
      type: "section",
      fields: [
        { type: "mrkdwn", text: `*Record:*\n${recordName}` },
        { type: "mrkdwn", text: `*Amount:*\n${amount || "N/A"}` },
        { type: "mrkdwn", text: `*Requested by:*\n${actorName || "System"}` },
      ],
    },
    {
      type: "actions",
      elements: [
        {
          type: "button",
          text: { type: "plain_text", text: "Approve" },
          style: "primary",
          action_id: "copilot_approve",
          value: JSON.stringify({ action: "approve", record: recordName }),
        },
        {
          type: "button",
          text: { type: "plain_text", text: "Reject" },
          style: "danger",
          action_id: "copilot_reject",
          value: JSON.stringify({ action: "reject", record: recordName }),
        },
        {
          type: "button",
          text: { type: "plain_text", text: "View in Odoo" },
          action_id: "copilot_view",
          url: `https://erp.insightpulseai.com/web#model=${recordName}`,
        },
      ],
    },
  ];
}

function buildTeamsCard(
  actionType: string,
  recordName: string,
  amount: string | number,
  actorName: string
) {
  return {
    type: "AdaptiveCard",
    $schema: "http://adaptivecards.io/schemas/adaptive-card.json",
    version: "1.4",
    body: [
      {
        type: "TextBlock",
        text: `Action Required: ${actionType}`,
        size: "Large",
        weight: "Bolder",
      },
      {
        type: "FactSet",
        facts: [
          { title: "Record", value: recordName },
          { title: "Amount", value: String(amount || "N/A") },
          { title: "Requested by", value: actorName || "System" },
        ],
      },
    ],
    actions: [
      {
        type: "Action.Submit",
        title: "Approve",
        data: { action: "approve", record: recordName },
      },
      {
        type: "Action.Submit",
        title: "Reject",
        data: { action: "reject", record: recordName },
      },
      {
        type: "Action.OpenUrl",
        title: "View in Odoo",
        url: `https://erp.insightpulseai.com/web#model=${recordName}`,
      },
    ],
  };
}
