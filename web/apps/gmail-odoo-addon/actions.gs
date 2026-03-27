/**
 * InsightPulseAI Gmail Add-on — Action Handlers
 *
 * Each function calls the corresponding Odoo bridge endpoint
 * and returns a notification card with the result.
 */

/**
 * Create a CRM lead from the current email context.
 */
function createLead(
  e
) {
  const params = e.commonEventObject.parameters || {};
  const senderEmail = params.sender_email || "";
  const subject = params.subject || "";

  const result = fetchBridge(API_PATHS.createLead, {
    sender_email: senderEmail,
    name: subject || `Lead from ${senderEmail}`,
  });

  if (result) {
    return notificationResponse(
      `Lead created: ${result.name || "OK"}`,
      String(result.url || "")
    );
  }

  return notificationResponse("Failed to create lead. Check connection.", "");
}

/**
 * Create a ticket (project.task) from the current email context.
 */
function createTicket(
  e
) {
  const params = e.commonEventObject.parameters || {};
  const senderEmail = params.sender_email || "";
  const subject = params.subject || "";

  const result = fetchBridge(API_PATHS.createTicket, {
    sender_email: senderEmail,
    name: subject || `Ticket from ${senderEmail}`,
  });

  if (result) {
    return notificationResponse(
      `Ticket created: ${result.name || "OK"}`,
      String(result.url || "")
    );
  }

  return notificationResponse("Failed to create ticket. Check connection.", "");
}

/**
 * Log a note to the matched partner's chatter.
 */
function logToChatter(
  e
) {
  const params = e.commonEventObject.parameters || {};
  const senderEmail = params.sender_email || "";
  const subject = params.subject || "";
  const partnerId = params.partner_id || "";

  const result = fetchBridge(API_PATHS.logNote, {
    sender_email: senderEmail,
    partner_id: partnerId ? parseInt(partnerId, 10) : false,
    body: `Gmail thread: ${subject}`,
  });

  if (result) {
    return notificationResponse("Note logged to chatter.", "");
  }

  return notificationResponse("Failed to log note. Check connection.", "");
}

/**
 * Open a record in Odoo (via OpenLink).
 */
function openInOdoo(
  e
) {
  const params = e.commonEventObject.parameters || {};
  const url = params.url || "https://erp.insightpulseai.com/web";

  return CardService.newActionResponseBuilder()
    .setOpenLink(CardService.newOpenLink().setUrl(url))
    .build();
}

/**
 * Build a notification card with an optional "Open in Odoo" link.
 */
function notificationResponse(
  message,
  url
) {
  const card = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle("InsightPulseAI"))
    .addSection(
      CardService.newCardSection()
        .addWidget(CardService.newTextParagraph().setText(message))
        .addWidget(
          url
            ? CardService.newTextButton()
                .setText("Open in Odoo")
                .setOpenLink(CardService.newOpenLink().setUrl(url))
            : CardService.newTextParagraph().setText("")
        )
    )
    .build();

  return CardService.newActionResponseBuilder()
    .setNavigation(CardService.newNavigation().pushCard(card))
    .build();
}
