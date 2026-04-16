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
#
# OUTPUT FORMAT: All output files are .docx (converted via pandoc).
# Readings for each session are combined into a single readings.docx.
# Homework drafts are saved as individual .docx files per assignment.
# Excel/spreadsheet assignments are flagged in REMINDERS — not auto-created.

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

## OUTPUT FORMAT
All output files are Word documents (.docx).
To create a .docx file:
1. Write the content as markdown to a temp file: /tmp/canvas_[[COURSE_CODE]]_[type].md
2. Convert with pandoc: pandoc /tmp/canvas_[[COURSE_CODE]]_[type].md -o "[output path].docx" --standalone
3. Delete the temp file: rm /tmp/canvas_[[COURSE_CODE]]_[type].md

---

## STEP 0 — DETERMINE SESSION & FOLDER

1. Call get_course_modules("[[COURSE_ID]]"). Find the module for the upcoming class.
   Identify the session number from the module title (e.g. "Session 5", "Week 3").
2. Session folder path: [[BASE_DIR]]/[[COURSE_CODE]]/Session-[NN]/
3. **Check if the folder already exists.**
   - If YES → this is an UPDATE run. Read existing prep.docx and readings.docx first,
     then merge new information in. Never delete existing content.
   - If NO → fresh run, create everything from scratch.

---

## STEP 1 — TRIANGULATE (course_id: [[COURSE_ID]])

Run all sources, then reconcile:

**A — Announcements:** get_announcements("[[COURSE_ID]]")
Read ALL announcements from the last 14 days. Note the posted_at timestamp on each.
On update runs, highlight anything newer than the last prep.docx modification.
Look for: reading changes, assignment clarifications, guest speakers, cold-call warnings,
any links or files mentioned in the body of the announcement.

**B — Syllabus:** get_syllabus("[[COURSE_ID]]")
Find this session's topic, listed readings, discussion questions, and due dates.

**C — Assignments:** get_course_assignments("[[COURSE_ID]]")
For each assignment due within 10 days:
- get_assignment_details → full description, rubric, word limits, submission type
- get_submission_status → skip if already submitted
- Note if submission_type suggests Excel/spreadsheet (file_upload with spreadsheet context)

**D — Modules:** get_course_modules("[[COURSE_ID]]") → get_module_items for this session's module.
List all items: pages, external URLs, files, assignments.

**RECONCILE** — build master table:
| Item | Found in | New since last run? |
|------|----------|-------------------|
Flag items in only one source as "(unconfirmed — check)".
Flag conflicts between announcements and syllabus — announcements win.

---

## STEP 2 — READINGS (combined into one document)

All readings for this session go into a **single combined document**: Session-[NN]/readings.docx

**If updating an existing session:** If readings.docx already exists, convert it back to markdown
with `pandoc readings.docx -o /tmp/existing_readings.md`, append new reading sections, then
reconvert. Never replace existing reading summaries — append an `## Updates — [timestamp]` section.

**If creating fresh:** Write all reading summaries sequentially in one markdown file, then convert.

For each confirmed reading in the master list:

- **Canvas page** → get_page_content(course_id, page_url)
- **External URL** → WebFetch. If paywalled → note: "🔒 Paywalled: [url]". If login required → "⚠️ Requires Stanford login"
- **Canvas file** → get_file_info(file_id) → note: "📎 Download: [filename] at [url]"
- **Physical book** → note: "📚 Textbook: [title] chapter X"

Combined document format (one section per reading, separated by horizontal rules):

```
# [[COURSE CODE]] — Session [NN] — Readings

---

# [Full Title of Reading 1]
**Source:** [Canvas page / URL / File]

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

---

# [Full Title of Reading 2]
...
```

Save to: Session-[NN]/readings.docx
(via /tmp/canvas_[[COURSE_CODE]]_readings.md → pandoc → readings.docx)

---

## STEP 3 — PREP BRIEF

Write/update: Session-[NN]/prep.docx
(via /tmp/canvas_[[COURSE_CODE]]_prep.md → pandoc → prep.docx)

**If creating fresh:**
```
# [[COURSE CODE]] — Session [NN]
**Class:** [date + time] [[ROOM]]
**Last updated:** [timestamp]

## What's Happening This Session
[2–3 sentence synthesis from all three sources. Note any conflicts.]

## Reconciliation Table
[master table from Step 1]

## Readings This Session
[One paragraph per reading: what it's about, what to pay attention to,
which discussion questions to keep in mind]
→ Full summaries: readings.docx

## Assignments Due
| Assignment | Due | Submitted? | Draft |
|------------|-----|------------|-------|

## Flagged
[Discrepancies, unconfirmed items, cold-call warnings, files to download manually]
```

**If updating:**
Prepend to the existing content (reconvert from docx first):
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

**Excel/spreadsheet assignments:**
- If the assignment description mentions Excel, spreadsheet, or the submission type is file_upload
  AND the context suggests a quantitative/model-building task:
  - Do NOT attempt to create an Excel file
  - Note in REMINDERS: "📊 Needs Excel work — [assignment name] — due [date]"
  - Write a .docx outline (Session-[NN]/drafts/[AssignmentName]-outline.docx) with:
    - The assignment prompt
    - Suggested sheet structure / tabs
    - Key formulas or calculations needed
    - Data sources from course readings

**All other assignments:**
- If submission_type is not online_text_entry but is NOT Excel:
  - Note in REMINDERS: "needs manual submission — [submission type]"
  - Still write a text draft as .docx for reference

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
Convert back with pandoc, then append:
```
## 🔄 Revision — [timestamp]
[What's new: instructor clarification from [date] announcement, revised approach to criterion X]
[Revised or additional content]
```
Do NOT delete the original draft.

**Draft format (write as markdown, then convert to .docx):**

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

Save to: Session-[NN]/drafts/[AssignmentName].docx
(via /tmp/canvas_[[COURSE_CODE]]_draft_[name].md → pandoc → [AssignmentName].docx)

---

## STEP 5 — UPDATE REMINDERS

File: [[BASE_DIR]]/REMINDERS.md

Find the existing [[COURSE_CODE]] session block and update it in place.
If no block exists yet, append:

```
## [[COURSE CODE]] — Session [NN] — updated [timestamp]

### Drafts Ready for Review
- [ ] [assignment] — due [date] — [[COURSE_CODE]]/Session-[NN]/drafts/[file].docx

### Needs Excel Work
- [ ] [assignment] — due [date] — see outline: [[COURSE_CODE]]/Session-[NN]/drafts/[file]-outline.docx

### Needs Manual Submission
- [ ] [assignment] — due [date] — [reason: file upload / etc.]

### Manual Reading Access Needed
- 📎 [filename] — download from Canvas Files
- 🔒 [title] — paywalled at [url]
- 📚 [title] — physical textbook chapter X

### Flagged
- [Discrepancies, cold-call warnings, unconfirmed readings]
```
