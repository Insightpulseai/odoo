import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
    if (req.method === "OPTIONS") {
        return new Response("ok", { headers: { "Access-Control-Allow-Origin": "*" } })
    }

    try {
        const { message, odoo } = await req.json()

        // Stub retrieval logic
        // In real implementation: 
        // 1. Embed `message` using OpenAI
        // 2. RPC call `docs.search_chunks`
        // 3. Generative answer via LLM

        const answer = `[STUB] I received your question: "${message}". \nContext: User ${odoo?.uid} on DB ${odoo?.db}. \n\nI am currently a stub backend. Please deploy the full RAG implementation.`

        const citations = [
            {
                title: "IPAI Copilot Stub",
                source: "supabase/functions/ipai-copilot/index.ts",
                url: "https://github.com/jgtolentino/odoo-ce",
                section: "Backend"
            }
        ]

        return new Response(
            JSON.stringify({ ok: true, answer, citations }),
            { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } },
        )
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), { status: 500, headers: { "Content-Type": "application/json" } })
    }
})
