// automations\main\static\js\project_activation.js
// Project activation management
let activeProjectId = null;

function toggleProjectActiveMode(projectId) {
    const btn = document.getElementById('activate-btn-' + projectId);
    const content = document.getElementById('project-content-' + projectId);
    
    if (!btn || !content) return;
    
    const isActive = btn.classList.contains('stop');
    
    if (!isActive) {
        // Activate
        btn.textContent = 'Stop';
        btn.className = 'activate-btn stop';
        content.classList.remove('locked');
        
        // Enable all interactive elements inside content
        const inputs = content.querySelectorAll('textarea, input, select, button:not(.activate-btn)');
        inputs.forEach(el => el.disabled = false);
        
        // Enter active mode globally
        document.querySelector('.layout').classList.add('active-mode');
        document.getElementById('bot-panel').classList.add('visible');
        
        activeProjectId = projectId;
        botLog('Session activated: ' + projectId);
        
        // Focus on first textarea if exists
        const firstTextarea = content.querySelector('textarea');
        if (firstTextarea) firstTextarea.focus();
        
    } else {
        // Deactivate
        btn.textContent = 'Activate';
        btn.className = 'activate-btn activate';
        content.classList.add('locked');
        
        // Disable all interactive elements inside content
        const inputs = content.querySelectorAll('textarea, input, select, button:not(.activate-btn)');
        inputs.forEach(el => el.disabled = true);
        
        // Exit active mode globally
        document.querySelector('.layout').classList.remove('active-mode');
        document.getElementById('bot-panel').classList.remove('visible');
        
        activeProjectId = null;
        botLog('Session deactivated.');
    }
}

function botLog(msg) {
    const out = document.getElementById('bot-output');
    if (!out) return;
    const ts = new Date().toLocaleTimeString();
    const cursorSpan = out.querySelector('.cursor');
    if (cursorSpan) cursorSpan.remove();
    const line = document.createElement('span');
    line.className = 'line';
    line.innerHTML = '<span class="timestamp">[' + ts + ']</span> $ ' + msg;
    out.appendChild(line);
    const newCursor = document.createElement('span');
    newCursor.className = 'cursor';
    out.appendChild(newCursor);
    out.scrollTop = out.scrollHeight;
}

function toggleSideConsole() {
    const panel = document.getElementById('bot-panel');
    const btn = panel.querySelector('.bot-toggle');
    const isCollapsed = panel.classList.toggle('collapsed');
    panel.classList.toggle('visible');
    btn.textContent = isCollapsed ? '◂' : '▸';
}

// Show toast notification
function showToast(msg, type, duration) {
    type = type || 'success';
    duration = duration || 3000;
    let el = document.getElementById('toast');
    if (!el) {
        el = document.createElement('div');
        el.id = 'toast';
        document.body.appendChild(el);
    }
    el.textContent = msg;
    el.className = 'toast ' + type;
    el.classList.add('visible');
    clearTimeout(el._timeout);
    el._timeout = setTimeout(function() { el.classList.remove('visible'); }, duration);
}

// Load navigation
function loadNavigation(currentProjectId) {
    fetch('/api/navigation')
        .then(r => r.json())
        .then(data => {
            const nav = document.getElementById('project-nav');
            nav.innerHTML = '';
            
            data.forEach(item => {
                const btn = document.createElement('button');
                btn.className = 'nav-btn';
                if (item.id === currentProjectId || (item.id === 'overview' && !currentProjectId)) {
                    btn.classList.add('active');
                }
                
                const iconSpan = document.createElement('span');
                iconSpan.textContent = item.icon || '•';
                iconSpan.style.marginRight = '8px';
                
                const textSpan = document.createElement('span');
                textSpan.textContent = item.name;
                
                btn.appendChild(iconSpan);
                btn.appendChild(textSpan);
                
                btn.addEventListener('click', () => {
                    if (document.querySelector('.layout.active-mode')) return;
                    if (item.url) {
                        window.location.href = item.url;
                    }
                });
                
                nav.appendChild(btn);
            });
        })
        .catch(error => {
            console.error('Failed to load navigation:', error);
            const nav = document.getElementById('project-nav');
            nav.innerHTML = '<button class="nav-btn active"><span>🏠</span> Overview</button>';
        });
}