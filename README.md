# Stanford Canvas × Claude

Automated class prep, reading summaries, and homework drafts — pulled straight from Canvas and delivered to your desktop before each class.

---

## What it does

For each of your courses, on a schedule you set, a Claude agent:

1. **Triangulates** your Canvas announcements, syllabus, and assignments section to build a complete picture of what's happening — catching readings posted only in announcements, assignment clarifications, schedule changes
2. **Reads and summarizes** every reading: key concepts, core arguments, connections to the course, and 5 discussion questions to be ready for in class
3. **Drafts homework** for any assignment due within 4 days — grounded in the actual course readings, structured to the rubric — saved locally for you to review and submit yourself
4. **Updates** each session folder if new announcements come in between runs, appending what changed without overwriting anything

Everything lives in session folders on your Desktop. Nothing auto-submits.

---

## Folder structure

```
Canvas <> Claude/
├── ACCT313/
│   ├── Session-05/
│   │   ├── prep.md          ← class brief
│   │   ├── readings/
│   │   │   └── HermanMiller-ProfitabilityAnalysis.md
│   │   └── drafts/
│   │       └── HermanMiller-Assignment.md   ← REVIEW BEFORE SUBMITTING
│   └── Session-06/
├── FINANCE347/
│   └── Session-05/
│       └── ...
├── (one folder per course)
└── REMINDERS.md             ← master checklist, auto-updated
```

---

## Requirements

- [Claude Desktop](https://claude.ai/download) with an active Claude subscription
- [Claude Code](https://claude.ai/claude-code) (for scheduling agents)
- Python 3.11+
- A Stanford Canvas API token
- macOS (paths use Unix conventions; Windows users will need to adjust paths)

---

## Setup

### 1. Get your Canvas API token

Go to **[canvas.stanford.edu](https://canvas.stanford.edu)** → Account (top-left) → Settings → scroll to **Approved Integrations** → **+ New Access Token**

- Purpose: anything you like (e.g. "Claude")
- Expiry: up to 120 days (you'll need to regenerate when it expires)

> **Token copy tip:** Canvas wraps long tokens across two lines in the UI. The hyphen at the end of the first line is a display artifact — do NOT include it when copying. Copy the whole token as one continuous string.

### 2. Clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/stanford-canvas-claude
cd stanford-canvas-claude
```

### 3. Install Python 3.11

```bash
brew install python@3.11
```

### 4. Create the virtualenv and install dependencies

```bash
cd canvas-mcp
python3.11 -m venv .venv
.venv/bin/pip install mcp httpx pydantic python-dotenv setuptools
.venv/bin/pip install -e .
```

### 5. Set your API token

```bash
cp .env.example .env
# Open .env and replace "your_token_here" with your actual token
open -a TextEdit .env
```

### 6. Test the connection

```bash
cd src
CANVAS_API_TOKEN=$(grep CANVAS_API_TOKEN ../.env | cut -d= -f2) \
  ../.venv/bin/python3 -c "
import asyncio
from canvas_api import CanvasAPI
async def test():
    api = CanvasAPI()
    p = await api.get_user_profile()
    print('Connected as:', p.get('name'))
    courses = await api.get_courses()
    for c in courses:
        print(f'  [{c[\"id\"]}] {c[\"name\"]}')
    await api.close()
asyncio.run(test())
"
```

You should see your name and a list of your active Canvas courses with their IDs. **Copy those IDs** — you'll need them in Step 8.

### 7. Add the MCP server to Claude Desktop

Open (or create) `~/Library/Application Support/Claude/claude_desktop_config.json` and add the `mcpServers` block:

```json
{
  "mcpServers": {
    "canvas": {
      "command": "/path/to/stanford-canvas-claude/canvas-mcp/.venv/bin/python3",
      "args": [
        "/path/to/stanford-canvas-claude/canvas-mcp/src/canvas_server.py"
      ],
      "env": {
        "CANVAS_API_TOKEN": "your_token_here",
        "CANVAS_BASE_URL": "https://canvas.stanford.edu"
      }
    }
  }
}
```

Replace `/path/to/stanford-canvas-claude` with the actual path where you cloned the repo.

**Quit and relaunch Claude Desktop** after saving. You should see a tools icon or "canvas" listed as an available MCP server.

### 8. Create your output folders

Create a folder on your Desktop called `Canvas <> Claude`, then inside it create one folder per course using the course code:

```bash
mkdir -p ~/Desktop/"Canvas <> Claude"/{ACCT313,FINANCE347,HRMGT350,POLECON230,STRAMGT329,STRAMGT351}
```

Adjust the course codes to match your actual courses.

### 9. Create scheduled tasks for each course

In Claude Desktop, open Claude Code and run `/schedule` to create a new scheduled task.

For each course, create one task using the template in `prompts/course-template.md`. Fill in:

| Placeholder | What to put |
|-------------|-------------|
| `[[COURSE CODE]]` | e.g. `ACCT 313` |
| `[[COURSE NAME]]` | e.g. `Financial Statement Analysis` |
| `[[COURSE_ID]]` | The Canvas course ID from Step 6 |
| `[[DAYS]]` | e.g. `Tue/Fri` |
| `[[TIME]]` | e.g. `2:50pm` |
| `[[ROOM]]` | e.g. `C106` |
| `[[BASE_DIR]]` | Full path to your `Canvas <> Claude` folder |

**Suggested schedule** (cron, local time):
- Class at 8–10am → run at `0 6 * * [days]`
- Class at 10am–2pm → run at `0 7 * * [days]`
- Class at 2pm+ → run at `0 7 * * [days]`

Where `[days]` in cron: Mon=1, Tue=2, Wed=3, Thu=4, Fri=5. Example: Mon+Thu = `1,4`

After creating each task, click **Run now** in the Scheduled sidebar once to pre-approve the Canvas tool permissions — this prevents future automated runs from pausing on permission prompts.

---

## Updating your token

Canvas tokens expire (Stanford caps them at 120 days). When yours expires:

1. Go to canvas.stanford.edu → Account → Settings → Approved Integrations → regenerate
2. Update the token in two places:
   - `canvas-mcp/.env`
   - `~/Library/Application Support/Claude/claude_desktop_config.json` (in the `env` block)
3. Restart Claude Desktop

---

## Hard rules (built into every agent prompt)

- **Never opens exams or quizzes** — any item whose name or type indicates it's a timed assessment is skipped and logged
- **Never auto-submits** — all drafts are saved locally with a `DRAFT — DO NOT SUBMIT WITHOUT REVIEWING` header; you submit manually
- **Update, don't overwrite** — if a session folder already exists, new runs append `🔄 Updated` sections rather than replacing files

---

## Canvas tools available

The MCP server exposes these tools to Claude:

| Tool | What it does |
|------|-------------|
| `get_courses` | All active courses |
| `get_announcements` | Announcements (per course or all) |
| `get_syllabus` | Full syllabus body |
| `get_course_assignments` | All assignments for a course |
| `get_assignment_details` | Full description, rubric, due date |
| `get_submission_status` | Whether you've submitted an assignment |
| `get_course_modules` | All modules |
| `get_module_items` | Items inside a module (pages, files, URLs) |
| `get_course_pages` | All wiki pages |
| `get_page_content` | Full text of a Canvas page |
| `get_course_files` | Files uploaded to a course |
| `get_file_info` | Download URL for a specific file |
| `get_discussion_topics` | Discussion prompts |
| `get_upcoming_assignments` | Assignments due soon (across all courses) |
| `get_calendar_events` | Calendar events in a date range |
| `get_grades` | Grade data |

---

## Resources

- [Canvas REST API docs](https://canvas.instructure.com/doc/api/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
