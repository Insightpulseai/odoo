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
function homepage() {
  var token = getOdooSession();
  if (!token) {
    return loginCard();
  }

  var summary = getSessionSummary();

  var header = CardService.newCardHeader()
    .setTitle("InsightPulseAI ERP")
    .setSubtitle("Odoo ERP Integration");

  // Connection status section
  var providerName = summary.provider
    ? PROVIDER_DISPLAY_NAMES[summary.provider]
    : "Unknown";

  var statusSection = CardService.newCardSection()
    .setHeader("Connection")
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel("Status")
        .setContent("Connected with " + providerName)
    );

  if (summary.userEmail) {
    statusSection.addWidget(
      CardService.newKeyValue()
        .setTopLabel("ERP account")
        .setContent(summary.userEmail)
    );
  }

  statusSection.addWidget(
    CardService.newKeyValue()
      .setTopLabel("ERP tenant")
      .setContent(summary.tenantDisplayName + "\n" + TENANT_CONFIG.odooBaseUrl.replace("https://", ""))
  );

  // Quick access section
  var accessSection = CardService.newCardSection()
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
          CardService.newOpenLink().setUrl(TENANT_CONFIG.odooBaseUrl + "/web")
        )
    );

  // Session actions section
  var actionsSection = CardService.newCardSection()
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
