---
name: referrals
description: "Gamified employee referral program with points, levels, rewards, and leaderboards."
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Referrals — Odoo 19.0 Skill Reference

## Overview

The **Referrals** app gamifies employee referrals by awarding points as referred candidates progress through the recruitment pipeline. Employees share job positions, track referral progress, earn points, level up with superhero avatars, and redeem points for configurable rewards. The app requires **Employees**, **Recruitment**, and **Website** to be installed.

## Key Concepts

- **Referral Points** — Earned when a referred applicant reaches a recruitment stage configured with "Show in Referrals". Points accumulate over the employee's lifetime.
- **Level** — Tier based on cumulative points. Each level has a name, point requirement, and avatar image. Leveling up changes the user's dashboard avatar. Levels are purely cosmetic.
- **Reward** — Prize redeemable with referral points (e.g., gift card, mug, extra day off). Each has a name, cost in points, description, photo, and gift responsible person.
- **Friend (Avatar)** — When a referral is hired, the referrer selects a superhero avatar for them. Friends appear on the referrer's dashboard (front or back position). Five preconfigured avatars.
- **Onboarding** — Four-slide introductory tutorial shown on first app access. Superhero-themed. Displays until user clicks "Start Now".
- **Alert** — Notification displayed on the Referrals dashboard to inform employees of referral program updates.
- **Share** — Mechanism for employees to share open job positions via social media, email, or direct link.
- **Referral Analysis** — Report showing referral statistics (points earned, hires, sources).

## Core Workflows

### 1. Configure Rewards

1. Navigate to `Referrals → Configuration → Rewards`, click **New**.
2. Enter Product Name, Cost (in points), Company (multi-company only), Gift Responsible.
3. Upload Photo and write Description.
4. Ensure cost > 0 to avoid free rewards.

### 2. Configure Recruitment Stages for Points

1. Navigate to `Recruitment → Configuration → Stages` (or edit stages from the Kanban).
2. On each desired stage, enable **Show in Referrals** and set the **Points** value.
3. When a referred applicant enters that stage, the referrer earns the configured points.

### 3. Share a Job Position (Employee)

1. Open the `Referrals` app.
2. Browse open job positions on the dashboard.
3. Click **Share** on a job to generate a unique referral link.
4. Share via social media (Facebook, X, LinkedIn), email, or copy the link.

### 4. Refer a Candidate

1. Share a job link with a candidate.
2. When the candidate applies via the referral link, the application is tagged with the referrer.
3. As the applicant progresses through pipeline stages, the referrer earns points.

### 5. Redeem Rewards

1. In the Referrals app, click **Rewards**.
2. Browse available rewards. Each card shows the point cost.
3. If sufficient points: click **Buy** → confirm in the popup.
4. Points are deducted. The Gift Responsible is notified to deliver the reward.

### 6. Level Up

1. Accumulate enough points to reach the next level threshold.
2. When ready, the dashboard shows "CLICK TO LEVEL UP!" with an animated graphic.
3. Click to level up. Avatar updates. Points are not consumed by leveling.

### 7. Manage Hired Referrals

1. When a referral is hired, the referrer sees a "Choose an avatar" screen on next app visit.
2. Select from five available superhero avatars. Previously chosen avatars are grayed out.
3. The avatar appears on the referrer's dashboard.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `hr.referral.reward` | Reward definition |
| `hr.referral.points` | Point transaction record |
| `hr.referral.level` | Level definition |
| `hr.referral.friend` | Hired referral avatar |
| `hr.referral.alert` | Dashboard alert |
| `hr.referral.onboarding` | Onboarding slide |

### Key Fields

- `hr.referral.reward`: `name`, `cost`, `company_id`, `gift_responsible_id`, `description`, `image`
- `hr.referral.level`: `name`, `requirements` (points needed), `image`
- `hr.referral.friend`: `name`, `position` (front/back), `image`, `dashboard_image`
- `hr.recruitment.stage`: `is_in_referral` (Show in Referrals), `points` (referral points for stage)

### Access Rights

| Level | Capabilities |
|-------|-------------|
| Referral User | Access Referrals dashboard, share jobs, redeem rewards |
| Officer | Above + view reports |
| Administrator | Full access including configuration, rewards, levels, onboarding, reports |

### Important Menu Paths

- `Referrals` — main dashboard with jobs, points, level, avatars
- `Referrals → Rewards` — reward shop
- `Referrals → Configuration → Rewards`
- `Referrals → Configuration → Levels`
- `Referrals → Configuration → Friends`
- `Referrals → Configuration → Onboarding`
- `Referrals → Configuration → Alerts`
- `Referrals → Reporting → Referral Analysis`
- `Referrals → Reporting → Rewards Report`
- `Referrals → Reporting → Points Report`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Points Report and Rewards Report added to Reporting menu.
- Onboarding slides are reorderable via drag-and-drop.
- Onboarding slides support per-company scoping in multi-company databases.
- Friend avatars support Front/Back positioning relative to the user's superhero avatar.
- Referral Analysis report available for Administrators.

## Common Pitfalls

- **Rewards with zero cost appear as free.** Always set a point cost > 0 for rewards.
- **Onboarding loops until "Start Now" is clicked.** Clicking "Skip" does not complete onboarding; slides reappear on next visit.
- **Points are lifetime cumulative for levels.** Spending points on rewards does not affect level progress. Points earned are tracked separately from points spent.
- **Image changes to friends/levels are irreversible.** Once saved, original images cannot be restored without reinstalling the app.
- **Requires Employees, Recruitment, AND Website.** All three apps must be installed for Referrals to function. Missing any one causes errors.
