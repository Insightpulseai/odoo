/**
 * notarize.js — electron-builder afterSign hook
 *
 * Submits the signed app to Apple's notarization service.
 * Called automatically by electron-builder after code signing.
 *
 * Prerequisites:
 *   export APPLE_ID="your@email.com"
 *   export APPLE_APP_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
 *   export APPLE_TEAM_ID="XXXXXXXXXX"
 *
 * Skips notarization when:
 *   - Running on non-macOS platforms
 *   - Environment variables are absent (dev/unsigned builds)
 */

const { notarize } = require('@electron/notarize');

module.exports = async function afterSign(context) {
  const { electronPlatformName, appOutDir } = context;

  // Only notarize on macOS
  if (electronPlatformName !== 'darwin') {
    return;
  }

  // Skip if credentials not configured (Branch B: unsigned builds)
  const appleId = process.env.APPLE_ID;
  const appleIdPassword = process.env.APPLE_APP_SPECIFIC_PASSWORD;
  const teamId = process.env.APPLE_TEAM_ID;

  if (!appleId || !appleIdPassword || !teamId) {
    console.log('Notarization skipped: APPLE_ID / APPLE_APP_SPECIFIC_PASSWORD / APPLE_TEAM_ID not set');
    return;
  }

  const appName = context.packager.appInfo.productFilename;
  const appPath = `${appOutDir}/${appName}.app`;

  console.log(`Notarizing ${appPath}...`);

  await notarize({
    appBundleId: 'com.insightpulseai.colima-desktop',
    appPath,
    appleId,
    appleIdPassword,
    teamId,
  });

  console.log(`Notarization complete: ${appPath}`);
};
