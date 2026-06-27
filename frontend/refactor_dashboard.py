import sys

with open(r"c:\Users\palfi\OneDrive\Attachments\Desktop\skillin\frontend\dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace style block
start_idx = content.find("<style>")
end_idx = content.find("</style>") + len("</style>")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + '<link rel="stylesheet" href="styles.css">' + content[end_idx:]

# Refactor classes
content = content.replace('class="header"', 'class="top-header"')
content = content.replace('class="category-grid"', 'class="grid-cards"')
content = content.replace('class="category-card"', 'class="card"')
content = content.replace('class="course-grid"', 'class="grid-cards-large"')
content = content.replace('class="course-card"', 'class="card course-card"')
content = content.replace('class="ai-grid"', 'class="grid-cards"')
content = content.replace('class="ai-card"', 'class="card ai-card"')
content = content.replace('class="mission"', 'class="card mission"')
content = content.replace('class="interview-modal"', 'class="modal-overlay"')
content = content.replace('class="interview-container"', 'class="modal-content"')
content = content.replace('class="btn-listen"', 'class="btn btn-primary btn-listen"')
content = content.replace('class="btn-submit"', 'class="btn btn-success btn-submit"')
content = content.replace('class="btn-close"', 'class="btn btn-danger btn-close"')
content = content.replace('class="score"', 'class="score-badge"')

# Add Theme Toggle Button
theme_btn = """
  <div class="header-right" style="display:flex; align-items:center; gap:16px;">
    <div class="score-badge" id="score">Skillin Score: 0</div>
    <button class="theme-toggle-btn" onclick="toggleTheme()"><i class="fas fa-moon"></i></button>
  </div>
"""
content = content.replace('<div class="score-badge" id="score">Skillin Score: 0</div>', theme_btn)

# Add Dark mode JS logic
js_logic = """
// Dark mode toggle
function toggleTheme() {
    const root = document.documentElement;
    const isDark = root.getAttribute('data-theme') === 'dark';
    root.setAttribute('data-theme', isDark ? 'light' : 'dark');
    localStorage.setItem('theme', isDark ? 'light' : 'dark');
}
// Init theme
if (localStorage.getItem('theme') === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
}
"""
content = content.replace('// ========== GLOBAL VARIABLES ==========', js_logic + '\n// ========== GLOBAL VARIABLES ==========')

with open(r"c:\Users\palfi\OneDrive\Attachments\Desktop\skillin\frontend\dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
print("done")
