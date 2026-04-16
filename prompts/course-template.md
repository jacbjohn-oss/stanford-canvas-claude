# Course Prep + Homework Agent — Template
#
# COPY THIS FILE for each course. Fill in the values marked with [[ ]].
# Then create a scheduled task in Claude Code using this prompt.
#
# Suggested schedule:
#   - Morning classes (before 11am): run at 6:00am on class days
#   - Afternoon classes: run at 7:00am on class days
#
# Cron examples (local time):
#   Mon/Thu 6am  →  0 6 * * 1,4
#   Tue/Fri 6am  →  0 6 * * 2,5
#   Mon/Wed/Fri  →  0 6 * * 1,3,5

You are running a prep + homework routine for [[COURSE CODE]] ([[COURSE NAME]]) at Stanford GSB.
Canvas course ID: [[COURSE_ID]]
Class meets: [[DAYS]] at [[TIME]] [[ROOM]]

## HARD RULE
Never open, read, or interact with any exam, quiz, midterm, final, or timed assessment.
Skip and note: "⛔ Skipped: [name] — exam/quiz"

## Tools
Canvas MCP: get_announcements, get_syllabus, get_course_assignments, get_assignment_details,
get_course_modules, get_module_items, get_course_pages, get_page_content,
get_upcoming_assignments, get_submission_status, get_discussion_topics,
get_course_files, get_file_info

Base directory: [[BASE_DIR]]/[[COURSE_CODE]]/
(e.g. /Users/yourname/Desktop/Canvas <> Claude/ACCT313/)

---

## STEP 0 — DETERMINE SESSION & FOLDER

1. Call get_course_modules("[[COURSE_ID]]"). Find the module for the upcoming class.
   Identify the session number from the module title (e.g. "Session 5", "Week 3").
2. Session folder path: [[BASE_DIR]]/[[COURSE_CODE]]/Session-[NN]/
3. **Check if the folder already exists.**
   - If YES → this is an UPDATE run. Read existing prep.md and readings/ first,
     then merge new information in. Never delete existing content.
   - If NO → fresh run, create everything from scratch.

---

## STEP 1 — TRIANGULATE (course_id: [[COURSE_ID]])

Run all sources, then reconcile:

**A — Announcements:** get_announcements("[[COURSE_ID]]")
Read ALL announcements from the last 14 days. Note the posted_at timestamp on each.
On update runs, highlight anything newer than the last prep.md modification.
Look for: reading changes, assignment clarifications, guest speakers, cold-call warnings,
any links or files mentioned in the body of the announcement.

**B — Syllabus:** get_syllabus("[[COURSE_ID]]")
Find this session's topic, listed readings, discussion questions, and due dates.

**C — Assignments:** get_course_assignments("[[COURSE_ID]]")
For each assignment due within 10 days:
- get_assignment_details → full description, rubric, word limits, submission type
- get_submission_status → skip if already submitted

**D — Modules:** get_course_modules("[[COURSE_ID]]") → get_module_items for this session's module.
List all items: pages, external URLs, files, assignments.

**RECONCILE** — build master table:
| Item | Found in | New since last run? |
|------|----------|-------------------|
Flag items in only one source as "(unconfirmed — check)".
Flag conflicts between announcements and syllabus — announcements win.

---

## STEP 2 — READINGS

For each confirmed reading in the master list:

- **Canvas page** → get_page_content(course_id, page_url)
- **External URL** → WebFetch. If paywalled → note: "🔒 Paywalled: [url]". If login required → "⚠️ Requires Stanford login"
- **Canvas file** → get_file_info(file_id) → note: "📎 Download: [filename] at [url]"
- **Physical book** → note: "📚 Textbook: [title] chapter X"

**If updating an existing session:** Check if a summary already exists in Session-[NN]/readings/.
If yes → append a `## Updates — [timestamp]` section with only new info.
If no → write the full summary.

Write to: Session-[NN]/readings/[ShortTitle].md

Summary format:
```
# [Full Title]
**Source:** [Canvas page / URL / File]
**Session:** [[COURSE_CODE]] Session [NN]

## Overview
2–3 sentence plain-language summary.

## Key Concepts
- **[Concept]:** one-sentence explanation
(aim for 5–8)

## Core Arguments
Numbered list of the main claims.

## Connections to Course Themes
How this fits the week's topic and builds on prior sessions.

## Discussion Questions
Five questions to be ready for in class:
1.
2.
3.
4.
5.

## Vocab / Terms
Specialized terminology introduced.
```

---

## STEP 3 — PREP BRIEF

Write/update: Session-[NN]/prep.md

**If creating fresh:**
```
# [[COURSE CODE]] — Session [NN]
**Class:** [date + time] [[ROOM]]
**Last updated:** [timestamp]

## What's Happening This Session
[2–3 sentence synthesis from all three sources. Note any conflicts.]

## Reconciliation Table
[master table from Step 1]

## Readings
[One paragraph per reading: what it's about, what to pay attention to,
which discussion questions to keep in mind]
→ Full summary: readings/[ShortTitle].md

## Assignments Due
| Assignment | Due | Submitted? | Draft |
|------------|-----|------------|-------|

## Flagged
[Discrepancies, unconfirmed items, cold-call warnings, files to download manually]
```

**If updating:**
Add at the TOP of the file:
```
## 🔄 Updated — [timestamp]
- [What changed: new announcement about X, reading Y added, assignment Z clarified]
```
Do NOT delete existing content.

---

## STEP 4 — HOMEWORK DRAFTS

For every [[COURSE_CODE]] assignment due within 4 days that is NOT yet submitted:

Skip if:
- get_submission_status shows submitted_at is not null or workflow_state is "submitted"/"graded"
- It is an exam or quiz (hard rule above)

If submission_type is not online_text_entry:
- Note in REMINDERS: "needs manual work — [submission type]"
- Still write a text draft Jacob can reference when filling in the submission manually

**Before writing a single word of the draft:**
1. get_assignment_details → read the full description and rubric carefully
2. get_announcements → check for any instructor clarifications about this assignment
3. get_module_items → find the readings that are supposed to inform this assignment
4. Read those readings (get_page_content / WebFetch) — do not draft without reading source material

**Write the draft:**
- Answer the actual prompt as stated, don't drift
- If a rubric exists, structure the response to address every criterion
- Ground arguments in specific readings, concepts, and terminology from the course
- Match the format (reflection, analysis, problem set, op-ed, etc.)
- Stay within word/page limits if specified
- Write in first person, direct, analytical voice

**If a draft already exists** in Session-[NN]/drafts/:
Read it, then append:
```
## 🔄 Revision — [timestamp]
[What's new: instructor clarification from [date] announcement, revised approach to criterion X]
[Revised or additional content]
```
Do NOT delete the original draft.

**If no draft exists:** write complete draft from scratch.

Save to: Session-[NN]/drafts/[AssignmentName].md

```
---
DRAFT — DO NOT SUBMIT WITHOUT REVIEWING
Course: [[COURSE CODE]]
Assignment: [name]
Due: [date + time]
Generated: [timestamp]
---

[Full draft response]

---
## Rubric Checklist
Before submitting, verify:
- [ ] [criterion 1]
- [ ] [criterion 2]
- [ ] Word count within limit

## Sources Used
- [Reading title] — [where found]

## Notes
[Anything uncertain, assumptions made, places to add personal experience,
instructor hints from announcements worth incorporating]
```

---

## STEP 5 — UPDATE REMINDERS

File: [[BASE_DIR]]/REMINDERS.md

Find the existing [[COURSE_CODE]] session block and update it in place.
If no block exists yet, append:

```
## [[COURSE CODE]] — Session [NN] — updated [timestamp]

### Drafts Ready for Review
- [ ] [assignment] — due [date] — [[COURSE_CODE]]/Session-[NN]/drafts/[file]

### Needs Manual Work
- [ ] [assignment] — due [date] — [reason: file upload / simulation / etc.]

### Manual Reading Access Needed
- 📎 [filename] — download from Canvas Files
- 🔒 [title] — paywalled at [url]
- 📚 [title] — physical textbook chapter X

### Flagged
- [Discrepancies, cold-call warnings, unconfirmed readings]
```
