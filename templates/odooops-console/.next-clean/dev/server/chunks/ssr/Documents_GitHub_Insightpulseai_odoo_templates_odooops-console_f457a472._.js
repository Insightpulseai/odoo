module.exports = [
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/src/lib/supabase/server.ts [app-rsc] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "createSupabaseServerClient",
    ()=>createSupabaseServerClient
]);
// src/lib/supabase/server.ts
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$headers$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/headers.js [app-rsc] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f40$supabase$2f$ssr$2f$dist$2f$module$2f$index$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/@supabase/ssr/dist/module/index.js [app-rsc] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f40$supabase$2f$ssr$2f$dist$2f$module$2f$createServerClient$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/@supabase/ssr/dist/module/createServerClient.js [app-rsc] (ecmascript)");
;
;
function createSupabaseServerClient() {
    const cookieStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$headers$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["cookies"])();
    const url = ("TURBOPACK compile-time value", "https://spdtwktxdalcfigzeqrz.supabase.co");
    const anon = ("TURBOPACK compile-time value", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2NDQwMzUsImV4cCI6MjA3NjIyMDAzNX0.IHBJ0cNTMKJvRozljqaEqWph_gC0zlW2Td5Xl_GENs4");
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f40$supabase$2f$ssr$2f$dist$2f$module$2f$createServerClient$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["createServerClient"])(url, anon, {
        cookies: {
            getAll () {
                return cookieStore.getAll();
            },
            setAll (cookiesToSet) {
                // NOTE: Next.js Server Components require us to set cookies via the cookieStore.
                cookiesToSet.forEach(({ name, value, options })=>{
                    cookieStore.set(name, value, options);
                });
            }
        }
    });
}
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/login/server-actions.ts [app-rsc] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// src/app/login/server-actions.ts
/* __next_internal_action_entry_do_not_use__ [{"40163562cf803cc8333dd0bc255df9b541be5f2650":"loginAction"},"",""] */ __turbopack_context__.s([
    "loginAction",
    ()=>loginAction
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$build$2f$webpack$2f$loaders$2f$next$2d$flight$2d$loader$2f$server$2d$reference$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/build/webpack/loaders/next-flight-loader/server-reference.js [app-rsc] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$api$2f$navigation$2e$react$2d$server$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/api/navigation.react-server.js [app-rsc] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$client$2f$components$2f$navigation$2e$react$2d$server$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/client/components/navigation.react-server.js [app-rsc] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$src$2f$lib$2f$supabase$2f$server$2e$ts__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/src/lib/supabase/server.ts [app-rsc] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$build$2f$webpack$2f$loaders$2f$next$2d$flight$2d$loader$2f$action$2d$validate$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/build/webpack/loaders/next-flight-loader/action-validate.js [app-rsc] (ecmascript)");
;
;
;
async function loginAction(formData) {
    const email = String(formData.get("email") || "").trim();
    const password = String(formData.get("password") || "");
    const next = String(formData.get("next") || "/app");
    if (!email || !password) {
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$client$2f$components$2f$navigation$2e$react$2d$server$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["redirect"])(`/login?next=${encodeURIComponent(next)}`);
    }
    const supabase = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$src$2f$lib$2f$supabase$2f$server$2e$ts__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["createSupabaseServerClient"])();
    const { error } = await supabase.auth.signInWithPassword({
        email,
        password
    });
    if (error) {
        // keep it simple; you can add error messaging later
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$client$2f$components$2f$navigation$2e$react$2d$server$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["redirect"])(`/login?next=${encodeURIComponent(next)}`);
    }
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$client$2f$components$2f$navigation$2e$react$2d$server$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["redirect"])(next);
}
;
(0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$build$2f$webpack$2f$loaders$2f$next$2d$flight$2d$loader$2f$action$2d$validate$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["ensureServerEntryExports"])([
    loginAction
]);
(0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$build$2f$webpack$2f$loaders$2f$next$2d$flight$2d$loader$2f$server$2d$reference$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["registerServerReference"])(loginAction, "40163562cf803cc8333dd0bc255df9b541be5f2650", null);
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/.next-internal/server/app/login/page/actions.js { ACTIONS_MODULE0 => \"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/login/server-actions.ts [app-rsc] (ecmascript)\" } [app-rsc] (server actions loader, ecmascript) <locals>", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$app$2f$login$2f$server$2d$actions$2e$ts__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/login/server-actions.ts [app-rsc] (ecmascript)");
;
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/.next-internal/server/app/login/page/actions.js { ACTIONS_MODULE0 => \"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/login/server-actions.ts [app-rsc] (ecmascript)\" } [app-rsc] (server actions loader, ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "40163562cf803cc8333dd0bc255df9b541be5f2650",
    ()=>__TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$app$2f$login$2f$server$2d$actions$2e$ts__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["loginAction"]
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f2e$next$2d$internal$2f$server$2f$app$2f$login$2f$page$2f$actions$2e$js__$7b$__ACTIONS_MODULE0__$3d3e$__$225b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$app$2f$login$2f$server$2d$actions$2e$ts__$5b$app$2d$rsc$5d$__$28$ecmascript$2922$__$7d$__$5b$app$2d$rsc$5d$__$28$server__actions__loader$2c$__ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i('[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/.next-internal/server/app/login/page/actions.js { ACTIONS_MODULE0 => "[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/login/server-actions.ts [app-rsc] (ecmascript)" } [app-rsc] (server actions loader, ecmascript) <locals>');
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$app$2f$login$2f$server$2d$actions$2e$ts__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/login/server-actions.ts [app-rsc] (ecmascript)");
}),
];

//# sourceMappingURL=Documents_GitHub_Insightpulseai_odoo_templates_odooops-console_f457a472._.js.map