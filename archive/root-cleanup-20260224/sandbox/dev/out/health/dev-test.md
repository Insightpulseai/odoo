# Health Check Report

**Environment:** `dev`  
**Timestamp:** `2026-02-16T15:12:41.553189`  
**Total Checks:** 13  

## Summary

| Status | Count |
|--------|-------|
| ✅ Passed | 3 |
| ❌ Failed | 4 |
| ⚠️  Warnings | 0 |
| ⏭️  Skipped | 6 |

## Detailed Results

### CLOUDFLARE

| Component | Status | Message | Duration (ms) |
|-----------|--------|---------|---------------|
| zone | ⏭️ SKIP | CLOUDFLARE_TOKEN or CLOUDFLARE_ZONE_ID not set | N/A |

### GITHUB

| Component | Status | Message | Duration (ms) |
|-----------|--------|---------|---------------|
| api-root | ✅ OK | HTTP 200 | 838.9 |

### MCP

| Component | Status | Message | Duration (ms) |
|-----------|--------|---------|---------------|
| discovery | ⏭️ SKIP | MCP_BASE_URLS not set or empty | N/A |

### N8N

| Component | Status | Message | Duration (ms) |
|-----------|--------|---------|---------------|
| healthz | ❌ FAIL | HTTPSConnectionPool(host='n8n.insightpulseai.net', port=443): Max retries exceeded with url: /healthz (Caused by NameResolutionError("HTTPSConnection(host='n8n.insightpulseai.net', port=443): Failed to resolve 'n8n.insightpulseai.net' ([Errno 8] nodename nor servname provided, or not known)")) | 233.0 |

### ODOO

| Component | Status | Message | Duration (ms) |
|-----------|--------|---------|---------------|
| web | ⏭️ SKIP | ODOO_BASE_URL not set | N/A |

### POSTGRES

| Component | Status | Message | Duration (ms) |
|-----------|--------|---------|---------------|
| connection | ❌ FAIL | invalid dsn: invalid URI query parameter: "supa"
 | 2.7 |

### SUPABASE

| Component | Status | Message | Duration (ms) |
|-----------|--------|---------|---------------|
| auth-health | ❌ FAIL | HTTP 401 (expected [200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399]) | 276.2 |
| postgrest | ✅ OK | HTTP 200 | 3966.0 |
| storage | ❌ FAIL | HTTP 400 (expected [200, 401, 403]) | 316.4 |
| rpc-smoke | ✅ OK | HTTP 404 | 302.7 |

### SUPERSET

| Component | Status | Message | Duration (ms) |
|-----------|--------|---------|---------------|
| health | ⏭️ SKIP | SUPERSET_BASE_URL not set | N/A |

### VERCEL

| Component | Status | Message | Duration (ms) |
|-----------|--------|---------|---------------|
| ops-console | ⏭️ SKIP | OPS-CONSOLE_URL not set | N/A |
| marketing | ⏭️ SKIP | MARKETING_URL not set | N/A |

---
⚠️ **Action Required:** Health check detected failures. Review failed checks above.