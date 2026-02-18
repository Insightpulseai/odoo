(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push(["chunks/[root-of-the-server]__0b6bc5cc._.js",
"[externals]/node:buffer [external] (node:buffer, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("node:buffer", () => require("node:buffer"));

module.exports = mod;
}),
"[externals]/node:async_hooks [external] (node:async_hooks, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("node:async_hooks", () => require("node:async_hooks"));

module.exports = mod;
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/src/lib/supabase/middleware.ts [middleware-edge] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "createSupabaseMiddlewareClient",
    ()=>createSupabaseMiddlewareClient
]);
// src/lib/supabase/middleware.ts
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$esm$2f$api$2f$server$2e$js__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/esm/api/server.js [middleware-edge] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$esm$2f$server$2f$web$2f$exports$2f$index$2e$js__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/esm/server/web/exports/index.js [middleware-edge] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f40$supabase$2f$ssr$2f$dist$2f$module$2f$index$2e$js__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/@supabase/ssr/dist/module/index.js [middleware-edge] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f40$supabase$2f$ssr$2f$dist$2f$module$2f$createServerClient$2e$js__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/@supabase/ssr/dist/module/createServerClient.js [middleware-edge] (ecmascript)");
;
;
function createSupabaseMiddlewareClient(req) {
    const res = __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$esm$2f$server$2f$web$2f$exports$2f$index$2e$js__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__["NextResponse"].next();
    const url = ("TURBOPACK compile-time value", "https://spdtwktxdalcfigzeqrz.supabase.co");
    const anon = ("TURBOPACK compile-time value", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2NDQwMzUsImV4cCI6MjA3NjIyMDAzNX0.IHBJ0cNTMKJvRozljqaEqWph_gC0zlW2Td5Xl_GENs4");
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    const supabase = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f40$supabase$2f$ssr$2f$dist$2f$module$2f$createServerClient$2e$js__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__["createServerClient"])(url, anon, {
        cookies: {
            getAll () {
                return req.cookies.getAll();
            },
            setAll (cookiesToSet) {
                cookiesToSet.forEach(({ name, value, options })=>{
                    res.cookies.set(name, value, options);
                });
            }
        }
    });
    return {
        supabase,
        res
    };
}
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/src/middleware.ts [middleware-edge] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "config",
    ()=>config,
    "middleware",
    ()=>middleware
]);
// src/middleware.ts
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$esm$2f$api$2f$server$2e$js__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/esm/api/server.js [middleware-edge] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$esm$2f$server$2f$web$2f$exports$2f$index$2e$js__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/esm/server/web/exports/index.js [middleware-edge] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$src$2f$lib$2f$supabase$2f$middleware$2e$ts__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/src/lib/supabase/middleware.ts [middleware-edge] (ecmascript)");
;
;
async function middleware(req) {
    const { supabase, res } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$src$2f$lib$2f$supabase$2f$middleware$2e$ts__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__["createSupabaseMiddlewareClient"])(req);
    // Refresh session if needed (cookie-based)
    const { data: { user } } = await supabase.auth.getUser();
    const isAppRoute = req.nextUrl.pathname.startsWith("/app");
    if (isAppRoute && !user) {
        const url = req.nextUrl.clone();
        url.pathname = "/login";
        url.searchParams.set("next", req.nextUrl.pathname);
        return __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$esm$2f$server$2f$web$2f$exports$2f$index$2e$js__$5b$middleware$2d$edge$5d$__$28$ecmascript$29$__["NextResponse"].redirect(url);
    }
    return res;
}
const config = {
    matcher: [
        "/app/:path*"
    ]
};
}),
]);

//# sourceMappingURL=%5Broot-of-the-server%5D__0b6bc5cc._.js.map