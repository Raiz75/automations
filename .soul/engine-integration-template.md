---
title: Engine Integration Template
aliases:
  - How to add an engine
  - New engine checklist
tags:
  - automations
  - template
  - tutorial
---

# Engine Integration Template

Use this checklist when adding a new engine to the project hub.

## 1. Create engine directory

```
automations/engine/<engine-name>/
├── __init__.py
└── engine.py              # Core logic, exports get_status() + functions
```

## 2. `automations/main/app.py` — Add to sys.path

```python
# After existing dirs
NEW_ENGINE_DIR = os.path.join(ENGINE_DIR, '<engine-name>')
sys.path.insert(0, NEW_ENGINE_DIR)
```

## 3. `automations/main/routes.py` — Four changes

### 3a. Add dir + sys.path (lines ~14-22)

```python
NEW_ENGINE_DIR = os.path.join(ENGINE_DIR, '<engine-name>')
sys.path.insert(0, NEW_ENGINE_DIR)
```

### 3b. Try-import with availability flag

```python
try:
    from engine import get_status, core_function
    NEW_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: New engine import error: {e}")
    NEW_ENGINE_AVAILABLE = False
```

### 3c. Add `PROJECTS_CONFIG` entry

```python
"<engine-id>": {
    "name": "<Display Name>",
    "icon": "?-icon",
    "url": "/<engine-route>",
    "template": "<engine-page>.html",
    "enabled": True
},
```

### 3d. Add page route + API routes inside `register_routes()`

```python
@app.route("/<engine-route>")
def <engine>_page():
    return render_template("<engine-page>.html", current_project_id="<engine-id>")

@app.route("/api/<engine-route>/status")
def <engine>_status():
    if NEW_ENGINE_AVAILABLE:
        return jsonify(get_status())
    return jsonify({"available": False, "error": "Engine not loaded"})

# Add any additional POST/GET routes the engine needs
```

## 4. Create page template `templates/<engine-page>.html`

```html
{% extends "_base.html" %}
{% block title %}Engine Title{% endblock %}
{% block content %}
{% import "_partials/project_header.html" as header %}
{% import "_partials/project_content.html" as content %}

{{ header.project_header(
    title="?- Icon Engine Name",
    description="Description text.",
    status_dot="checking",
    status_label="checking engine...",
    activate_text="Activate",
    project_id="<engine-id>"
) }}

{% call content.project_content("<engine-id>") %}
    <!-- Engine UI controls here -->
{% endcall %}
{% endblock %}

{% block scripts %}
<script>
    function checkStatus() {
        fetch("/api/<engine-route>/status")
            .then(r => r.json())
            .then(s => {
                const dot = document.querySelector('.status-dot');
                const label = document.querySelector('.status-dot-label');
                if (s.available) {
                    dot.className = 'status-dot online';
                    label.textContent = 'engine ready';
                } else {
                    dot.className = 'status-dot offline';
                    label.textContent = 'engine offline';
                }
            })
            .catch(() => {
                document.querySelector('.status-dot').className = 'status-dot offline';
                document.querySelector('.status-dot-label').textContent = 'error';
            });
    }
    document.addEventListener("DOMContentLoaded", checkStatus);
</script>
{% endblock %}
```

## 5. `templates/index.html` — Add overview card

```html
<div style="...">
    <h3 style="...">?- Icon Engine Name</h3>
    <p>Short description.</p>
    <button onclick="window.location.href='/<engine-route>'">Try it now</button>
</div>
```

## 6. `style.css` — Add dark mode overrides (end of file)

```css
/* Engine Name dark mode */
#custom-element-id {
    background: #0d0d1a !important;
    color: #aaa !important;
}
```

## 7. `requirements.txt` — Append new dependencies

## 8. `.soul/` — Add engine doc

Create `<engine-name>.md` describing architecture, API, and flow.

## Auto-generated (no manual changes needed)

| File | Why |
|---|---|
| `_base.html` | Sidebar populated from `/api/navigation` (auto-derived from `PROJECTS_CONFIG`) |
| `project_header.html` | Consumes parameters, no per-engine code |
| `project_content.html` | Generic wrapper, no per-engine code |
| `bot_panel.html` | Fixed global partial |
| `project_activation.js` | All functions use dynamic IDs (`activate-btn-{id}`, `project-content-{id}`) |

## Key globals available in page JS

| Function | Source |
|---|---|
| `botLog(msg)` | `project_activation.js` — logs to bot console |
| `showToast(msg)` | `project_activation.js` — shows toast notification |
| `toggleProjectActiveMode(id)` | `project_activation.js` — toggles locked/unlocked |
