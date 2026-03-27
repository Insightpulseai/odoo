/**
 * InsightPulseAI Gmail Add-on — Homepage
 *
 * Entry point rendered when the add-on sidebar is opened
 * outside the context of a specific email message.
 * Shows explicit connected-state with provider, tenant, and session actions.
 */

/**
 * Homepage trigger function (referenced in appsscript.json).
 */
function homepage(): GoogleAppsScript.Card_Service.Card {
  const token = getOdooSession();
  if (!token) {
    return loginCard();
  }

  const summary = getSessionSummary();

  const header = CardService.newCardHeader()
    .setTitle("InsightPulseAI ERP")
    .setSubtitle("Odoo ERP Integration");

  // Connection status section
  const providerName = summary.provider
    ? PROVIDER_DISPLAY_NAMES[summary.provider]
    : "Unknown";

  const statusSection = CardService.newCardSection()
    .setHeader("Connection")
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel("Status")
        .setText(`Connected with ${providerName}`)
    );

  if (summary.userEmail) {
    statusSection.addWidget(
      CardService.newKeyValue()
        .setTopLabel("ERP account")
        .setText(summary.userEmail)
    );
  }

  statusSection.addWidget(
    CardService.newDecoratedText()
      .setTopLabel("ERP tenant")
      .setText(`${summary.tenantDisplayName}\n${TENANT_CONFIG.odooBaseUrl.replace("https://", "")}`)
  );

  // Quick access section
  const accessSection = CardService.newCardSection()
    .setHeader("Quick Access")
    .addWidget(
      CardService.newTextParagraph().setText(
        "Open an email to see matched contacts, leads, and tickets from your Odoo ERP."
      )
    )
    .addWidget(
      CardService.newTextButton()
        .setText("Open Odoo ERP")
        .setOpenLink(
          CardService.newOpenLink().setUrl(`${TENANT_CONFIG.odooBaseUrl}/web`)
        )
    );

  // Session actions section
  const actionsSection = CardService.newCardSection()
    .setHeader("Session")
    .addWidget(
      CardService.newTextButton()
        .setText("Switch sign-in method")
        .setOnClickAction(
          CardService.newAction().setFunctionName("handleDisconnect")
        )
    )
    .addWidget(
      CardService.newTextButton()
        .setText("Disconnect")
        .setOnClickAction(
          CardService.newAction().setFunctionName("handleDisconnect")
        )
    );

  return CardService.newCardBuilder()
    .setHeader(header)
    .addSection(statusSection)
    .addSection(accessSection)
    .addSection(actionsSection)
    .build();
}
