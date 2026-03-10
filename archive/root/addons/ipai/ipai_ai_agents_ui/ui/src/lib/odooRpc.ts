/**
 * IPAI AI Agents UI - Odoo JSON-RPC Helper
 *
 * Helper function for making JSON-RPC calls to Odoo endpoints.
 * Uses the same session authentication as the Odoo web client.
 */

/**
 * Make a JSON-RPC call to an Odoo endpoint.
 *
 * @param route - The endpoint route (e.g., "/ipai_ai_agents/bootstrap")
 * @param params - Parameters to pass to the endpoint
 * @returns The result from the JSON-RPC response
 * @throws Error if the request fails or returns an error
 */
export async function odooJsonRpc(
  route: string,
  params: Record<string, unknown>
): Promise<unknown> {
  const response = await fetch(route, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "same-origin", // Include session cookies
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "call",
      params,
      id: Math.floor(Math.random() * 1000000),
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
  }

  const data = await response.json();

  // Check for JSON-RPC error
  if (data.error) {
    const errorMessage =
      data.error.data?.message ||
      data.error.message ||
      "Unknown error occurred";
    throw new Error(errorMessage);
  }

  return data.result;
}
