# Python Project Hub — Flask Landing Page

## Purpose
A Flask-powered landing page that serves as a visual hub for Python projects. Visitors can browse projects from a side panel and view details on demand without page reloads.

## Tech Stack
- **Backend:** Flask (Python)
- **Frontend:** Vanilla HTML + CSS + JavaScript (no frameworks)
- **Data:** Hardcoded Python list of dicts

## Project Structure
```
automations/
├── app.py              # Flask app with API endpoints + hardcoded project data
├── templates/
│   └── index.html      # Single page: side panel + content area
└── static/
    └── style.css       # Minimal clean styling
```

## API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Serves `index.html` |
| GET | `/api/projects` | Returns JSON list of projects (id + name) for side panel |
| GET | `/api/projects/<id>` | Returns full JSON details for a single project |

## Project Data Model
```python
{
    "id": "str",
    "name": "str",
    "description": "str",
    "tech_stack": ["str"],
    "github_url": "str"
}
```

## Frontend Layout
Two-column flex layout:
- **Side panel:** Fixed 220px width, light gray background, vertical nav buttons listing project names
- **Content area:** Remaining width, initially shows a welcome/heading message

## Behavior
1. On page load, JS fetches `GET /api/projects` and renders buttons in the side panel
2. Clicking a nav button fetches `GET /api/projects/<id>` and updates the content area
3. Active button is highlighted; content fades in smoothly
4. No full page reloads — all updates happen via vanilla JS

## Style
Minimal and clean: light theme, ample whitespace, subtle borders, sans-serif font.
