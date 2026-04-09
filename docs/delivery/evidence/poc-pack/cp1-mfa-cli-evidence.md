# CP-1 MFA Evidence — CLI Verification

**Date**: 2026-03-20
**Method**: Microsoft Graph PowerShell (Connect-MgGraph)

## Security Defaults
- **Status**: Enabled (isEnabled=True)

## Admin Authentication Methods

### admin@insightpulseai.com (Platform Admin)
- Password: Enrolled (ID: 28c10230-6103-485e-b985-444c60001490)
- Microsoft Authenticator: Enrolled (ID: 5c7c98d1-22c1-4fff-807b-e46778b6abb7)
- **MFA Status**: ENROLLED

### emergency-admin@insightpulseai.com (Emergency Admin)
- Password: Enrolled (ID: 28c10230-6103-485e-b985-444c60001490)
- Microsoft Authenticator: NOT enrolled
- **MFA Status**: NOT ENROLLED — registration campaign enabled, will be forced on next sign-in

## Registration Campaign
- State: enabled
- Target: all_users → microsoftAuthenticator
- Snooze: 1 day, enforce after allowed snoozes

## Roles Verified
- admin@insightpulseai.com: Global Administrator
- emergency-admin@insightpulseai.com: Global Administrator
- ceo@insightpulseai.com (external MSA): Global Administrator + 1 other

## Verdict
- CP-1: **PARTIAL** — 1 of 2 native admin accounts has MFA enrolled
- emergency-admin@ will be forced to enroll on next interactive sign-in
