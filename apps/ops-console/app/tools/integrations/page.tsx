import { redirect } from "next/navigation"

// /tools/integrations is a thin alias for the existing /integrations page.
// Redirect preserves the canonical route while allowing the new taxonomy to link here.
export default function ToolsIntegrationsPage() {
  redirect("/integrations")
}
