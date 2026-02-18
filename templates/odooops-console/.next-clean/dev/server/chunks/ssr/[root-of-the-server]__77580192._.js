module.exports = [
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/favicon.ico.mjs { IMAGE => \"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/favicon.ico (static in ecmascript, tag client)\" } [app-rsc] (structured image object, ecmascript, Next.js Server Component)", ((__turbopack_context__) => {

__turbopack_context__.n(__turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/favicon.ico.mjs { IMAGE => \"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/favicon.ico (static in ecmascript, tag client)\" } [app-rsc] (structured image object, ecmascript)"));
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/twitter-image.png.mjs { IMAGE => \"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/twitter-image.png (static in ecmascript, tag client)\" } [app-rsc] (structured image object, ecmascript, Next.js Server Component)", ((__turbopack_context__) => {

__turbopack_context__.n(__turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/twitter-image.png.mjs { IMAGE => \"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/twitter-image.png (static in ecmascript, tag client)\" } [app-rsc] (structured image object, ecmascript)"));
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/opengraph-image.png.mjs { IMAGE => \"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/opengraph-image.png (static in ecmascript, tag client)\" } [app-rsc] (structured image object, ecmascript, Next.js Server Component)", ((__turbopack_context__) => {

__turbopack_context__.n(__turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/opengraph-image.png.mjs { IMAGE => \"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/opengraph-image.png (static in ecmascript, tag client)\" } [app-rsc] (structured image object, ecmascript)"));
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/layout.tsx [app-rsc] (ecmascript, Next.js Server Component)", ((__turbopack_context__) => {

__turbopack_context__.n(__turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/layout.tsx [app-rsc] (ecmascript)"));
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/(auth)/layout.tsx [app-rsc] (ecmascript, Next.js Server Component)", ((__turbopack_context__) => {

__turbopack_context__.n(__turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/(auth)/layout.tsx [app-rsc] (ecmascript)"));
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/(auth)/login/page.tsx [app-rsc] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>LoginPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/server/route-modules/app-page/vendored/rsc/react-jsx-dev-runtime.js [app-rsc] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$api$2f$navigation$2e$react$2d$server$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/api/navigation.react-server.js [app-rsc] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$client$2f$components$2f$navigation$2e$react$2d$server$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/node_modules/next/dist/client/components/navigation.react-server.js [app-rsc] (ecmascript)");
(()=>{
    const e = new Error("Cannot find module '@/utils/supabase/server'");
    e.code = 'MODULE_NOT_FOUND';
    throw e;
})();
(()=>{
    const e = new Error("Cannot find module './LoginClient'");
    e.code = 'MODULE_NOT_FOUND';
    throw e;
})();
;
;
;
;
async function LoginPage({ searchParams }) {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    // If already authenticated, redirect to app
    if (user) {
        const params = await searchParams;
        const next = params?.next || "/";
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$client$2f$components$2f$navigation$2e$react$2d$server$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["redirect"])(next);
    }
    const params = await searchParams;
    const next = params?.next || "/";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$Insightpulseai$2f$odoo$2f$templates$2f$odooops$2d$console$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$rsc$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$rsc$5d$__$28$ecmascript$29$__["jsxDEV"])(LoginClient, {
        next: next
    }, void 0, false, {
        fileName: "[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/(auth)/login/page.tsx",
        lineNumber: 23,
        columnNumber: 10
    }, this);
}
}),
"[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/(auth)/login/page.tsx [app-rsc] (ecmascript, Next.js Server Component)", ((__turbopack_context__) => {

__turbopack_context__.n(__turbopack_context__.i("[project]/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console/app/(auth)/login/page.tsx [app-rsc] (ecmascript)"));
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__77580192._.js.map