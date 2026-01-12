/**
 * Superset Embed API - Self-signed JWT Guest Token Service
 *
 * This service generates guest tokens for embedding Superset dashboards
 * using the self-signed JWT pattern (no Superset API call required).
 *
 * The token is signed with the same secret configured in Superset:
 * - SUPERSET_GUEST_TOKEN_SECRET
 * - SUPERSET_GUEST_TOKEN_AUDIENCE
 *
 * Production URLs:
 * - https://superset-embed-api.insightpulseai.net
 * - Superset: https://superset.insightpulseai.net
 */
import express from "express";
import cors from "cors";
import jwt from "jsonwebtoken";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Configuration
const config = {
  secret: process.env.SUPERSET_GUEST_TOKEN_SECRET,
  audience: process.env.SUPERSET_GUEST_TOKEN_AUDIENCE || "superset",
  supersetDomain:
    process.env.SUPERSET_DOMAIN || "https://superset.insightpulseai.net",
  tokenExpirySeconds: parseInt(process.env.TOKEN_EXPIRY_SECONDS || "3600", 10),
  allowedOrigins: (
    process.env.ALLOWED_ORIGINS ||
    "https://erp.insightpulseai.net,https://scout-mvp.vercel.app,http://localhost:8069,http://localhost:3000"
  )
    .split(",")
    .map((o) => o.trim()),
  nodeEnv: process.env.NODE_ENV || "development",
};

// Validate required config
if (!config.secret) {
  console.error("FATAL: SUPERSET_GUEST_TOKEN_SECRET is required");
  process.exit(1);
}

// CORS configuration
app.use(
  cors({
    origin: (origin, callback) => {
      // Allow requests with no origin (e.g., Postman, curl)
      if (!origin) return callback(null, true);
      if (config.allowedOrigins.includes(origin)) {
        return callback(null, true);
      }
      return callback(new Error(`Origin ${origin} not allowed by CORS`));
    },
    credentials: true,
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  })
);

app.use(express.json());

/**
 * Health check endpoint
 */
app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    mode:
      config.nodeEnv === "production"
        ? "production (self-signed JWT)"
        : "development",
    timestamp: new Date().toISOString(),
  });
});

/**
 * Generate guest token for Superset dashboard embedding
 *
 * Query params:
 *   - dashboard_id: Superset dashboard UUID (required)
 *
 * Body (optional):
 *   - user: { username, first_name, last_name }
 *   - rls_rules: [{ clause: "..." }]
 */
app.get("/api/superset-token", (req, res) => {
  const dashboardId = req.query.dashboard_id;

  if (!dashboardId) {
    return res.status(400).json({
      error: "dashboard_id query parameter is required",
    });
  }

  const token = generateGuestToken({
    dashboardId: String(dashboardId),
    user: {
      username: "embedded_user",
      first_name: "Embedded",
      last_name: "User",
    },
    rlsRules: [],
  });

  res.json({
    token,
    embedUrl: `${config.supersetDomain}/embedded/${dashboardId}`,
    supersetDomain: config.supersetDomain,
    audience: config.audience,
    expiresAt: Math.floor(Date.now() / 1000) + config.tokenExpirySeconds,
  });
});

/**
 * POST version with full control over user and RLS
 */
app.post("/api/superset-token", (req, res) => {
  const { dashboard_id, user, rls_rules } = req.body;

  if (!dashboard_id) {
    return res.status(400).json({
      error: "dashboard_id is required in request body",
    });
  }

  const token = generateGuestToken({
    dashboardId: String(dashboard_id),
    user: user || {
      username: "embedded_user",
      first_name: "Embedded",
      last_name: "User",
    },
    rlsRules: rls_rules || [],
  });

  res.json({
    token,
    embedUrl: `${config.supersetDomain}/embedded/${dashboard_id}`,
    supersetDomain: config.supersetDomain,
    audience: config.audience,
    expiresAt: Math.floor(Date.now() / 1000) + config.tokenExpirySeconds,
  });
});

/**
 * Generate a self-signed JWT guest token
 *
 * @param {Object} options
 * @param {string} options.dashboardId - Superset dashboard UUID
 * @param {Object} options.user - User info {username, first_name, last_name}
 * @param {Array} options.rlsRules - RLS rules [{clause: "..."}]
 * @returns {string} Signed JWT token
 */
function generateGuestToken({ dashboardId, user, rlsRules }) {
  const now = Math.floor(Date.now() / 1000);

  const payload = {
    user: {
      username: user.username || "embedded_user",
      first_name: user.first_name || "Embedded",
      last_name: user.last_name || "User",
    },
    resources: [
      {
        type: "dashboard",
        id: dashboardId,
      },
    ],
    rls_rules: rlsRules || [],
    iat: now,
    exp: now + config.tokenExpirySeconds,
    aud: config.audience,
    type: "guest",
  };

  return jwt.sign(payload, config.secret, { algorithm: "HS256" });
}

// Error handler
app.use((err, req, res, next) => {
  console.error("Error:", err.message);
  res.status(500).json({ error: err.message });
});

// Start server
app.listen(PORT, () => {
  console.log(`Superset Embed API running on port ${PORT}`);
  console.log(`Mode: ${config.nodeEnv}`);
  console.log(`Superset domain: ${config.supersetDomain}`);
  console.log(`Allowed origins: ${config.allowedOrigins.join(", ")}`);
});
