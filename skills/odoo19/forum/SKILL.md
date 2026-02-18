---
name: forum
description: Odoo Forum for Q&A and community discussions with karma-based gamification
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# forum -- Odoo 19.0 Skill Reference

## Overview

Odoo Forum is a Q&A and discussion platform designed primarily for customer support and community engagement. It features karma-based gamification (ranks, badges, challenges), moderation tools, tagging, voting, and best-answer marking. Forums can be integrated with eLearning courses and Helpdesk tickets. Karma points are shared across all forums, courses, and websites within a single Odoo database.

## Key Concepts

- **Forum**: A discussion space configured under `Website > Configuration > Forum: Forums`. Each forum has its own mode, sorting, privacy, karma settings, and tags.
- **Mode**: `Questions` (allows marking a best answer, posts appear as solved/unsolved) or `Discussions` (no best-answer feature).
- **Post**: A question or discussion thread created by a user. Only one answer per user per post. Multiple comments allowed.
- **Karma Points**: Numeric score earned through forum interactions. Determines which features a user can access. Shared across all forums, courses, and websites on the same database. New users receive 3 points upon email validation.
- **Karma Gains**: Configurable point awards/penalties per interaction (asking, upvote, downvote, accepting answer, answer accepted, flagged).
- **Karma-Related Rights**: Configurable karma thresholds for accessing features (ask, answer, upvote, downvote, edit, close, delete, moderate, create tags, etc.).
- **Ranks**: Titles assigned to users based on total karma points (configurable name, required karma, description, motivational message, image).
- **Badges**: Awards granted manually (by authorized users) or automatically (via challenges). Optional levels: Bronze, Silver, Gold.
- **Challenges**: Automated criteria that, when met, grant badges to users.
- **Tags**: Labels for filtering forum posts. Managed via `Website > Configuration > Forum: Tags`. Users can create new tags when posting if they have sufficient karma.
- **Privacy**: `Public` (anyone), `Signed In` (logged-in users only), or `Some users` (specific access group).
- **Default Sort**: Newest, Last Updated, Most Voted, Relevance, or Answered.
- **Moderation Tools**: Sidebar tools for validating pending posts, handling flagged content, and managing closed questions.
- **Close Reasons**: Configurable reasons for closing posts. Types: `Basic` (general close) or `Offensive` (for flagged posts). Closing for spam/offensive deducts 100 karma.
- **Flagging**: Marking a post as offensive. Deducts 100 karma from the poster. Hidden from non-moderators.

## Core Workflows

### 1. Create a Forum

1. Go to `Website > Configuration > Forum: Forums`, click `New`.
2. Set `Forum Name`.
3. Select `Mode`: `Questions` (enable best answer marking) or `Discussions`.
4. Choose `Default Sort` (Newest, Last Updated, Most Voted, Relevance, Answered).
5. Set `Privacy`: Public, Signed In, or Some users (select Authorized Group).
6. Configure `Karma Gains` tab: adjust point values for each interaction.
7. Configure `Karma Related Rights` tab: set karma thresholds for each feature.
8. Save.

### 2. Post and Interact

1. Access the forum on the frontend, click `New Post`.
2. Enter `Title`, `Description`, and up to 5 `Tags`.
3. Click `Post Your Question`.
4. Other users can:
   - Vote up/down on questions and answers.
   - Mark an answer as best (Questions mode only, check mark button).
   - Favorite a question (star button).
   - Follow a post for notifications (bell button).
   - Comment on questions/answers (speech bubble button).
   - Share on social media.
   - Edit, close, delete, flag, or convert comments to answers (via ellipsis menu).

### 3. Moderate a Forum

1. Access the forum frontend. Moderator tools appear in the sidebar.
2. **To Validate**: Review pending questions/answers from users with insufficient karma. Approve or reject.
3. **Flagged**: Review posts flagged as offensive. Click `Accept` to remove the flag or `Offensive` to confirm (select a reason, deducts 100 karma from poster).
4. **Closed**: Review closed questions. Options: `Delete` or `Reopen`.
5. Bulk management: `Website > Configuration > Forum: Forums`, select forum, click `Posts` smart button. Use `Actions` to export, archive, unarchive, or delete.

### 4. Set Up Gamification (Ranks and Badges)

1. **Ranks**: Go to `Website > Configuration > Forum: Ranks`, click `New`. Set `Rank Name`, `Required Karma`, `Description`, `Motivational` message, and image.
2. **Badges (manual)**: Go to `Website > Configuration > Forum: Badges`, click `New`. Set name, description, image. Choose `Allowance to Grant` (Everyone, selected users, or users with specific badges). Optionally enable `Monthly Limited Sending`.
3. **Badges (automatic)**: Set `Allowance to Grant` to `No one, assigned through challenges`. Add challenges in the `Rewards for challenges` section.
4. Assign optional `Forum Badge Level` (Bronze, Silver, Gold) to badges.

### 5. Manage Tags

1. Go to `Website > Configuration > Forum: Tags`, click `New`.
2. Enter tag name and select the related `Forum`.
3. Users can also create tags when posting (requires sufficient karma, default 30 points).
4. Tags appear in the forum sidebar for filtering. Click `View all` to see all tags.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `forum.forum` | Forum configuration |
| `forum.post` | Forum post (question, answer) |
| `forum.tag` | Forum tag |
| `forum.post.reason` | Close reason |
| `gamification.badge` | Badge definition |
| `gamification.challenge` | Challenge definition (for automatic badge granting) |
| `gamification.karma.rank` | Karma rank |
| `gamification.karma.tracking` | Karma tracking (developer mode: `Settings > Gamification Tools > Karma Tracking`) |

### Key Fields

- `forum.forum`: `name`, `mode` (question/discussion), `default_order`, `privacy` (public/connected/authorized), `authorized_group_id`, `karma_*` fields (gains and rights thresholds), `website_id`
- `forum.post`: `name`, `forum_id`, `tag_ids`, `state`, `is_correct` (best answer), `vote_count`, `create_uid`
- `forum.tag`: `name`, `forum_id`

### Default Karma Gains

| Interaction | Default Points |
|-------------|---------------|
| Asking a question | +2 |
| Question upvoted | +5 |
| Question downvoted | -2 |
| Answer upvoted | +10 |
| Answer downvoted | -2 |
| Accepting an answer | +2 |
| Answer accepted | +15 |
| Answer flagged | -100 |
| Email validation | +3 |

### Default Karma Rights (Selected)

| Feature | Default Karma |
|---------|--------------|
| Ask/Answer questions | 3 |
| Upvote | 5 |
| Downvote | 50 |
| Edit own posts | 1 |
| Edit all posts | 300 |
| Close own posts | 100 |
| Close all posts | 500 |
| Delete own posts | 500 |
| Delete all posts | 1,000 |
| Moderate posts | 1,000 |
| Create new tags | 30 |
| Accept answer on own questions | 20 |
| Accept answer on all questions | 500 |
| Flag as offensive | 500 |
| Editor features (images/links) | 30 |
| Display detailed biography | 750 |
| View another user's profile | 150 (website-level default) |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Forum integrates with eLearning for per-course dedicated forums (requires `Forum` setting enabled in eLearning settings).
- Helpdesk ticket links visible from forum posts via ellipsis menu (`View` related ticket).
- Close reasons support two types: `Basic` and `Offensive`.
- Karma tracking available via developer mode under `Settings > Gamification Tools > Karma Tracking`.
- One answer per user per post enforced across both Questions and Discussions modes.

## Common Pitfalls

- **Karma is global**: Points are shared across all forums, courses, and websites on the same database. High karma thresholds on one forum affect a user's effective access on other forums too.
- **Sensitive moderation rights**: Features like `Edit all posts`, `Close all posts`, `Delete all posts`, and `Moderate posts` are powerful. Setting low karma thresholds grants these capabilities to too many users.
- **One pending question per user per forum**: If moderation is enabled and a user's post is pending, they cannot submit another question on that forum until the first is validated.
- **Flagging and closing penalties**: Flagging as offensive or closing for spam/offensive reasons deducts 100 karma from the poster -- this is a significant penalty that can lock users out of features.
- **nofollow on links**: Users below the `Nofollow links` karma threshold (default 500) have their links tagged with `nofollow`, which affects SEO value of links they post.
