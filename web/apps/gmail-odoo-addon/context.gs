/**
 * InsightPulseAI Gmail Add-on — Contextual Trigger
 *
 * Fires when a Gmail message is opened. Extracts the sender email,
 * queries the Odoo bridge for matching contact/records, and renders
 * action cards.
 */

/**
 * Gmail contextual trigger (referenced in appsscript.json).
 */
function onGmailMessage(
  e
) {
  const token = getOdooSession();
  if (!token) {
    return loginCard();
  }

  // Extract sender email from the open message
  const messageId = e.gmail?.messageId;
  if (!messageId) {
    return errorCard("Could not read the current message.");
  }

  const message = GmailApp.getMessageById(messageId);
  const senderRaw = message.getFrom();
  const senderEmail = extractEmail(senderRaw);
  const subject = message.getSubject();

  // Query bridge for context
  const result = fetchBridge(API_PATHS.context, {
    sender_email: senderEmail,
    subject,
  });

  if (!result) {
    return noMatchCard(senderEmail);
  }

  return contextCard(senderEmail, subject, result);
}

/**
 * Extract a bare email address from a "Name <email>" string.
 */
function extractEmail(raw) {
  const match = raw.match(/<([^>]+)>/);
  return match ? match[1] : raw.trim();
}

/**
 * Render the main context card with matched records and actions.
 */
function contextCard(
  senderEmail,
  subject,
  data
) {
  const partner = data.partner || null;
  const leads = data.leads || [];
  const tickets = data.tickets || [];
  const tasks = data.tasks || [];

  const header = CardService.newCardHeader()
    .setTitle("InsightPulseAI")
    .setSubtitle(senderEmail);

  const builder = CardService.newCardBuilder().setHeader(header);

  // Contact section
  if (partner) {
    const contactSection = CardService.newCardSection().setHeader("Contact");
    contactSection.addWidget(
      CardService.newKeyValue()
        .setTopLabel("Name")
        .setContent(String(partner.name || "Unknown"))
    );
    if (partner.company) {
      contactSection.addWidget(
        CardService.newKeyValue()
          .setTopLabel("Company")
          .setContent(String(partner.company))
      );
    }
    if (partner.phone) {
      contactSection.addWidget(
        CardService.newKeyValue()
          .setTopLabel("Phone")
          .setContent(String(partner.phone))
      );
    }
    builder.addSection(contactSection);
  }

  // Leads section
  if (leads.length > 0) {
    const leadsSection = CardService.newCardSection().setHeader(
      `Leads (${leads.length})`
    );
    for (const lead of leads.slice(0, 5)) {
      leadsSection.addWidget(
        CardService.newKeyValue()
          .setTopLabel(String(lead.stage || ""))
          .setContent(String(lead.name || ""))
          .setOnClickAction(
            CardService.newAction()
              .setFunctionName("openInOdoo")
              .setParameters({ url: String(lead.url || "") })
          )
      );
    }
    builder.addSection(leadsSection);
  }

  // Tickets / Tasks section
  const combined = [...tickets, ...tasks];
  if (combined.length > 0) {
    const ticketSection = CardService.newCardSection().setHeader(
      `Tickets / Tasks (${combined.length})`
    );
    for (const item of combined.slice(0, 5)) {
      ticketSection.addWidget(
        CardService.newKeyValue()
          .setTopLabel(String(item.stage || item.state || ""))
          .setContent(String(item.name || ""))
          .setOnClickAction(
            CardService.newAction()
              .setFunctionName("openInOdoo")
              .setParameters({ url: String(item.url || "") })
          )
      );
    }
    builder.addSection(ticketSection);
  }

  // Action buttons
  const actionsSection = CardService.newCardSection().setHeader("Actions");

  actionsSection.addWidget(
    CardService.newTextButton()
      .setText("Create Lead")
      .setOnClickAction(
        CardService.newAction()
          .setFunctionName("createLead")
          .setParameters({ sender_email: senderEmail, subject })
      )
  );

  actionsSection.addWidget(
    CardService.newTextButton()
      .setText("Create Ticket")
      .setOnClickAction(
        CardService.newAction()
          .setFunctionName("createTicket")
          .setParameters({ sender_email: senderEmail, subject })
      )
  );

  actionsSection.addWidget(
    CardService.newTextButton()
      .setText("Log to Chatter")
      .setOnClickAction(
        CardService.newAction()
          .setFunctionName("logToChatter")
          .setParameters({
            sender_email: senderEmail,
            subject,
            partner_id: String(partner?.id || ""),
          })
      )
  );

  if (partner && partner.url) {
    actionsSection.addWidget(
      CardService.newTextButton()
        .setText("Open in Odoo")
        .setOpenLink(
          CardService.newOpenLink().setUrl(String(partner.url))
        )
    );
  }

  builder.addSection(actionsSection);

  return builder.build();
}

/**
 * Card shown when no matching contact is found.
 */
function noMatchCard(
  senderEmail
) {
  const header = CardService.newCardHeader()
    .setTitle("InsightPulseAI")
    .setSubtitle("No match found");

  const section = CardService.newCardSection()
    .addWidget(
      CardService.newTextParagraph().setText(
        `No contact found for ${senderEmail} in Odoo.`
      )
    )
    .addWidget(
      CardService.newTextButton()
        .setText("Create Lead")
        .setOnClickAction(
          CardService.newAction()
            .setFunctionName("createLead")
            .setParameters({ sender_email: senderEmail, subject: "" })
        )
    );

  return CardService.newCardBuilder()
    .setHeader(header)
    .addSection(section)
    .build();
}

/**
 * Generic error card.
 */
function errorCard(message) {
  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle("Error"))
    .addSection(
      CardService.newCardSection().addWidget(
        CardService.newTextParagraph().setText(message)
      )
    )
    .build();
}
