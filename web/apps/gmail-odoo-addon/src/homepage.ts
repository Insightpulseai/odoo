/**
 * InsightPulseAI Gmail Add-on — Homepage
 *
 * Entry point rendered when the add-on sidebar is opened
 * outside the context of a specific email message.
 */

/**
 * Homepage trigger function (referenced in appsscript.json).
 */
function homepage(): GoogleAppsScript.Card_Service.Card {
  const token = getOdooSession();
  if (!token) {
    return loginCard();
  }

  const openErpAction = CardService.newAction().setFunctionName("openErpLink");

  const header = CardService.newCardHeader()
    .setTitle("InsightPulseAI")
    .setSubtitle("Odoo ERP Integration");

  const summarySection = CardService.newCardSection()
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
          CardService.newOpenLink().setUrl("https://erp.insightpulseai.com/web")
        )
    );

  return CardService.newCardBuilder()
    .setHeader(header)
    .addSection(summarySection)
    .build();
}
