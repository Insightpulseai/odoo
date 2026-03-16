---
name: surveys
description: Survey, assessment, and certification application with live sessions, scoring, conditional logic, and detailed response analysis.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# surveys — Odoo 19.0 Skill Reference

## Overview

The Surveys application enables creation of surveys, questionnaires, assessments, certifications, and live session interactive polls. Supports multiple question types (multiple choice, text input, numerical, date, datetime, matrix), conditional display logic, scoring with pass/fail thresholds, certification with badge awarding, randomized question selection, time limits, and real-time live session hosting. Used by marketing, HR, and training teams to collect feedback, evaluate knowledge, and measure satisfaction.

## Key Concepts

- **Survey**: The core record containing questions, options, and configuration. Survey type radio buttons: Survey, Live Session, Assessment, Custom (default, shows all options).
- **Section**: A visual divider that groups related questions within a survey. Supports randomized question picking per section.
- **Question Type**: The input format for a question: Multiple choice (single/multiple answer), Multiple Lines Text Box, Single Line Text Box, Numerical Value, Date, Datetime, Matrix.
- **Scoring**: Point values assigned to answers. Modes: No scoring, Scoring with answers after each page, Scoring with answers at the end, Scoring without answers.
- **Required Score (%)**: Minimum percentage to pass. Determines pass/fail status.
- **Certification**: A scored survey with the "Is a Certification" option enabled. Awards a PDF certificate and optionally a badge. Represented by a trophy icon on the dashboard.
- **Live Session**: A host-moderated real-time survey where participants answer questions simultaneously, and results are displayed as bar graphs via the Session Manager. Requires a Session Code.
- **Session Manager**: The host/moderator interface for Live Session surveys, controlling question progression and displaying real-time results.
- **Conditional Display**: Questions shown only when specific Triggering Answers from previous questions are selected.
- **Pagination**: Layout options — One page per question, One page per section, or One page with all questions.
- **Access Mode**: Controls who can take the survey — Anyone with the link, or Invited people only.
- **Participation**: A record of a participant's survey attempt, including answers and scores.

## Core Workflows

### 1. Create a Survey

1. Navigate to Surveys app, click **New**.
2. Select a survey type radio button (Survey, Live Session, Assessment, or Custom).
3. Enter a survey name (required).
4. Set the **Responsible** user.
5. Optionally upload a background image.
6. In the **Questions** tab, click **Add a question** to open the Create Sections and Questions popup.
7. Enter the question text, select Question Type, configure Answers tab (choices, correct answers, scores, images).
8. Configure Options tab: Answers section (comments, placeholders, validation), Constraints (Mandatory Answer), Conditional Display (Triggering Answers), Live Sessions (Question Time Limit).
9. Click **Save & Close** or **Save & New**.
10. Add sections with **Add a section** for organization.
11. Configure the **Options** tab on the survey form: Pagination, Question Selection, Time & Scoring, Participants, Live Session settings.
12. Add optional **Description** and **End Message** tabs.

### 2. Configure Scoring and Certification

1. In the survey's **Options** tab > Time & Scoring section, select a Scoring option (with/without answers).
2. Set **Required Score (%)** — the pass threshold.
3. Enable **Is a Certification** for certificate awarding.
4. Select a certification PDF template (with Preview option).
5. Configure **Certified Email Template** for automatic email delivery to passing participants.
6. Optionally enable **Give Badge** to award a badge on the participant's portal.
7. In Questions, mark correct answers in the Answers tab and assign Score values.

### 3. Share and Distribute a Survey

1. Click **Share** on the survey form or dashboard.
2. Copy the **Survey Link** (available when Access Mode = Anyone with the link).
3. Toggle **Send by Email** to add Recipients, Additional Emails, Subject, and send invitations.
4. Set an optional **Answer deadline**.
5. Click **Send** to dispatch email invitations.

### 4. Run a Live Session

1. Create a survey with the Live Session type (or Custom with appropriate options).
2. In Options > Live Session section, set a **Session Code**.
3. Share the Session Link with participants.
4. Click **Create Live Session** — opens the Session Manager in a new tab.
5. Wait for participants to join (counter shows attendees).
6. Click **Start** to begin. Each question is presented one at a time.
7. Monitor the progress bar as participants submit answers.
8. Click **Show Results** to display the bar graph of responses.
9. Click **Show Correct Answer(s)** to highlight correct (green) and incorrect (red) responses.
10. Click **Next** to advance to the next question.
11. Click **Close Live Session** on the survey form when complete.

### 5. Analyze Survey Results

1. Click **See results** on the survey dashboard line or survey form.
2. View the **Results Overview** summary at the top.
3. Filter by: All Surveys / Completed surveys, and Passed and Failed / Passed only / Failed only.
4. Each question shows Responded/Skipped counts and visual results (Pie graph for single-answer, Bar graph for multi-answer).
5. Switch between **Graph** and **Data** tabs for each question.
6. Click the filter icon on answer choices to filter all results by that specific response.
7. Navigate to Participations smart button for individual participant detail pages.
8. Global participation view: Surveys > Participations.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `survey.survey` | Survey record |
| `survey.question` | Survey question |
| `survey.question.answer` | Answer option for a question |
| `survey.user_input` | Participation/attempt record |
| `survey.user_input.line` | Individual answer line within a participation |

### Key Fields (survey.survey)

- `title` — Survey name (required)
- `user_id` — Responsible user
- `survey_type` — survey, live_session, assessment, custom
- `questions_layout` — one_page, page_per_section, page_per_question
- `questions_selection` — all, random
- `scoring_type` — no_scoring, scoring_with_answers, scoring_without_answers, scoring_with_answers_after_page
- `scoring_success_min` — Required score percentage
- `certification` — Is a Certification flag
- `certification_mail_template_id` — Email template for certified participants
- `certification_give_badge` — Award badge flag
- `is_time_limited` — Time limit enabled
- `time_limit` — Time limit in minutes
- `access_mode` — public (anyone with link), token (invited only)
- `users_login_required` — Require login
- `is_attempts_limited` — Limit attempts
- `attempts_limit` — Maximum attempts
- `session_code` — Live session access code
- `session_link` — Auto-generated session URL

### Key Fields (survey.question)

- `title` — Question text
- `question_type` — simple_choice, multiple_choice, text_box, char_box, numerical_box, date, datetime, matrix
- `constr_mandatory` — Mandatory answer flag
- `triggering_answer_ids` — Conditional display trigger answers
- `is_time_limited` — Per-question time limit (Live Session)
- `time_limit` — Time limit in seconds

### Key Menu Paths

- `Surveys` — Main dashboard (Kanban/List/Activities views)
- `Surveys > Questions & Answers > Questions` — All questions across surveys
- `Surveys > Participations` — All participations across surveys
- `Surveys > [Survey] > See results` — Visual results page
- `Surveys > [Survey] > Participations` smart button — Survey-specific participations

### Survey Dashboard Buttons

| Button | Action |
|--------|--------|
| Share | Open share popup with link and email options |
| Test | Take a test version of the survey |
| See results | View graphical results analysis |
| Start Live Session | Initiate live session mode |
| End Live Session | Close active live session |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18.0 vs 19.0 breaking changes documented -->

## Common Pitfalls

- **Certification and Live Session are mutually exclusive**: If "Is a Certification" is enabled, the survey cannot be used as a Live Session.
- **Session Code recommended for Live Sessions**: Without a Session Code, the Session Link URL is complex and participants can access the survey without a host, defeating the purpose of a live session.
- **Randomized per Section hides Conditional Display**: The Conditional Display option is not available when questions are randomly picked from sections.
- **Survey Time Limit does not apply to Live Sessions**: Only per-question time limits (set in the question's Options tab) work with Live Session surveys.
- **Allow Roaming not available in Live Sessions**: Participants cannot navigate back to previous questions during live sessions since the host controls the flow.
