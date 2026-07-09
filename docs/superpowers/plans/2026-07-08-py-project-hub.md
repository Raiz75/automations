# Python Project Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Flask landing page with a side panel navigation that displays Python project details on click.

**Architecture:** Flask backend with two JSON API endpoints. Vanilla HTML/CSS/JS frontend in a single-page layout. All project data hardcoded in Python.

**Tech Stack:** Flask, vanilla JavaScript, CSS

## Global Constraints

- Zero external frontend dependencies (no jQuery, no Bootstrap, no htmx)
- All project data hardcoded as Python list of dicts
- Side panel = left column, content = right column
- Minimal clean style: light theme, sans-serif font

---

### Task 1: Flask app with project data + API endpoints

**Files:**
- Create: `automations/app.py`
- Create: `automations/requirements.txt`

**Interfaces:**
- Produces: Flask app with two endpoints — `GET /api/projects` returns `List[Dict]` with id/name, `GET /api/projects/<id>` returns `Dict` with full project details, `GET /` serves `index.html`

- [ ] **Step 1: Create requirements.txt**

```txt
flask>=3.0
```

- [ ] **Step 2: Write `app.py` with project data and endpoints**

```python
from flask import Flask, jsonify, render_template

app = Flask(__name__)

PROJECTS = [
    {
        "id": "web-scraper",
        "name": "Web Scraper",
        "description": "A CLI tool that scrapes websites and extracts structured data into CSV or JSON formats. Supports pagination, custom selectors, and rate limiting.",
        "tech_stack": ["Python", "BeautifulSoup", "Requests", "SQLite"],
        "github_url": "https://github.com/user/web-scraper",
    },
    {
        "id": "cli-todo",
        "name": "CLI Todo Manager",
        "description": "A terminal-based todo list app with categories, priorities, due dates, and persistent storage via JSON files.",
        "tech_stack": ["Python", "argparse", "json"],
        "github_url": "https://github.com/user/cli-todo",
    },
    {
        "id": "data-viz",
        "name": "Data Viz Dashboard",
        "description": "A web dashboard that reads CSV files and generates interactive charts using Plotly for data exploration.",
        "tech_stack": ["Python", "Flask", "Plotly", "Pandas"],
        "github_url": "https://github.com/user/data-viz",
    },
    {
        "id": "file-sorter",
        "name": "File Sorter",
        "description": "Automatically organizes files in a directory by type (images, docs, audio, etc.) into categorized folders.",
        "tech_stack": ["Python", "pathlib", "shutil"],
        "github_url": "https://github.com/user/file-sorter",
    },
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/projects")
def list_projects():
    return jsonify([{"id": p["id"], "name": p["name"]} for p in PROJECTS])


@app.route("/api/projects/<project_id>")
def get_project(project_id):
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if project is None:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project)


if __name__ == "__main__":
    app.run(debug=True)
```

- [ ] **Step 3: Verify app starts**

Run: `cd automations && pip install -r requirements.txt && python app.py`
Expected: Server starts on `http://127.0.0.1:5000` without errors. Press Ctrl+C to stop.

---

### Task 2: HTML template with side panel + content area + JavaScript

**Files:**
- Create: `automations/templates/index.html`

**Interfaces:**
- Consumes: Flask `GET /api/projects` and `GET /api/projects/<id>` endpoints (Task 1)
- Produces: A single HTML page with side panel nav (left) and content area (right), wired with vanilla JS

- [ ] **Step 1: Create `templates/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Project Hub</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="layout">
        <aside class="sidebar">
            <h1 class="sidebar-title">Python Hub</h1>
            <nav id="project-nav" class="nav"></nav>
        </aside>
        <main class="content" id="content">
            <div class="welcome">
                <h2>Welcome to Python Project Hub</h2>
                <p>Select a project from the sidebar to view details.</p>
            </div>
        </main>
    </div>
    <script>
        const nav = document.getElementById("project-nav");
        const content = document.getElementById("content");

        fetch("/api/projects")
            .then((r) => r.json())
            .then((projects) => {
                projects.forEach((p) => {
                    const btn = document.createElement("button");
                    btn.className = "nav-btn";
                    btn.textContent = p.name;
                    btn.dataset.id = p.id;
                    btn.addEventListener("click", () => loadProject(p.id));
                    nav.appendChild(btn);
                });
            });

        function loadProject(id) {
            document.querySelectorAll(".nav-btn").forEach((b) => b.classList.remove("active"));

            const btn = document.querySelector(`.nav-btn[data-id="${id}"]`);
            if (btn) btn.classList.add("active");

            fetch(`/api/projects/${id}`)
                .then((r) => r.json())
                .then((project) => {
                    content.innerHTML = `
                        <div class="project-detail">
                            <h2>${project.name}</h2>
                            <p class="description">${project.description}</p>
                            <div class="section">
                                <h3>Tech Stack</h3>
                                <div class="tech-list">
                                    ${project.tech_stack.map((t) => `<span class="tech-tag">${t}</span>`).join("")}
                                </div>
                            </div>
                            <a href="${project.github_url}" class="github-link" target="_blank">View on GitHub</a>
                        </div>
                    `;
                });
        }
    </script>
</body>
</html>
```

---

### Task 3: CSS styling

**Files:**
- Create: `automations/static/style.css`

- [ ] **Step 1: Create `static/style.css`**

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #333;
    background: #fafafa;
    height: 100vh;
}

.layout {
    display: flex;
    height: 100vh;
}

.sidebar {
    width: 220px;
    min-width: 220px;
    background: #f0f0f0;
    border-right: 1px solid #ddd;
    padding: 24px 16px;
    overflow-y: auto;
}

.sidebar-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #222;
}

.nav {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.nav-btn {
    display: block;
    width: 100%;
    padding: 10px 14px;
    background: none;
    border: 1px solid transparent;
    border-radius: 6px;
    text-align: left;
    font-size: 14px;
    cursor: pointer;
    color: #444;
    transition: background 0.15s, border-color 0.15s;
}

.nav-btn:hover {
    background: #e4e4e4;
}

.nav-btn.active {
    background: #fff;
    border-color: #ccc;
    font-weight: 500;
    color: #222;
}

.content {
    flex: 1;
    padding: 40px;
    overflow-y: auto;
}

.welcome {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    color: #888;
}

.welcome h2 {
    font-size: 24px;
    color: #555;
    margin-bottom: 8px;
}

.project-detail h2 {
    font-size: 26px;
    color: #222;
    margin-bottom: 12px;
}

.project-detail .description {
    font-size: 15px;
    line-height: 1.6;
    color: #555;
    margin-bottom: 24px;
}

.section {
    margin-bottom: 24px;
}

.section h3 {
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #888;
    margin-bottom: 8px;
}

.tech-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.tech-tag {
    background: #e8e8e8;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 13px;
    color: #555;
}

.github-link {
    display: inline-block;
    padding: 10px 20px;
    background: #222;
    color: #fff;
    text-decoration: none;
    border-radius: 6px;
    font-size: 14px;
    transition: background 0.15s;
}

.github-link:hover {
    background: #444;
}
```

---

### Task 4: Final smoke test

- [ ] **Step 1: Verify everything works end-to-end**

Run: `cd automations && python app.py`
Expected: Navigate to `http://127.0.0.1:5000` — sidebar shows project buttons, clicking one fetches and displays project details on the right. Welcome message shows initially.
