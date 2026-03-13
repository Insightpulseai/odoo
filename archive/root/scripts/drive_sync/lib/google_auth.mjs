import { google } from "googleapis";

const SCOPES = [
  "https://www.googleapis.com/auth/drive.readonly",
  "https://www.googleapis.com/auth/documents.readonly"
];

export async function getGoogleAuth() {
  // Primary: Service account
  const saEmail = process.env.GOOGLE_CLIENT_EMAIL;
  const saKey = process.env.GOOGLE_PRIVATE_KEY;
  const impersonate = process.env.GOOGLE_IMPERSONATE_USER;

  if (saEmail && saKey) {
    const key = saKey.replace(/\\n/g, "\n");
    const jwt = new google.auth.JWT({
      email: saEmail,
      key,
      scopes: SCOPES,
      subject: impersonate || undefined
    });
    await jwt.authorize();
    return jwt;
  }

  // Fallback: OAuth refresh token
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const refreshToken = process.env.GOOGLE_REFRESH_TOKEN;

  if (clientId && clientSecret && refreshToken) {
    const oauth2 = new google.auth.OAuth2(clientId, clientSecret);
    oauth2.setCredentials({ refresh_token: refreshToken });
    await oauth2.getAccessToken();
    return oauth2;
  }

  throw new Error(
    "No Google auth configured. Provide either GOOGLE_CLIENT_EMAIL + GOOGLE_PRIVATE_KEY (+ optional GOOGLE_IMPERSONATE_USER) or GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET + GOOGLE_REFRESH_TOKEN."
  );
}
