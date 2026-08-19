#!/usr/bin/env python3
"""
build_preview.py
Inlines partials (nav/footer) and style.css directly into each page,
producing self-contained preview files (for quickly checking appearance in chat).

Not needed for actual deployment — Cloudflare Pages/GitHub Pages are
full server environments where fetch()-based partial includes work
normally, using the original modular files in the solacehouse/ directory.
"""
import re
import base64
from pathlib import Path

ROOT = Path(__file__).parent
PREVIEW_DIR = ROOT / "preview"
PREVIEW_DIR.mkdir(exist_ok=True)

nav_html = (ROOT / "partials" / "nav.html").read_text()
footer_html = (ROOT / "partials" / "footer.html").read_text()
style_css = (ROOT / "assets" / "css" / "style.css").read_text()

pages = ["index.html", "about.html", "focus-areas.html", "services.html", "testimonials.html", "book.html", "privacy.html"]

def inline_images(html):
    """Replace <img src="assets/img/xxx.png"> with a base64 data URI,
    for preview only, so images display in chat without needing directory access."""
    def replacer(match):
        rel_path = match.group(1)
        img_path = ROOT / rel_path
        if not img_path.exists():
            return match.group(0)
        data = base64.b64encode(img_path.read_bytes()).decode()
        ext = img_path.suffix.lstrip('.')
        mime = 'jpeg' if ext == 'jpg' else ext
        return f'src="data:image/{mime};base64,{data}"'
    return re.sub(r'src="(assets/img/[^"]+)"', replacer, html)

for page in pages:
    src = ROOT / page
    if not src.exists():
        continue
    html = src.read_text()

    # Inline CSS: replace <link rel="stylesheet" href="assets/css/style.css"> with <style>...</style>
    html = re.sub(
        r'<link rel="stylesheet" href="assets/css/style\.css">',
        f'<style>\n{style_css}\n</style>',
        html
    )

    # Inline nav / footer partials
    html = html.replace('<div data-include="nav"></div>', nav_html)
    html = html.replace('<div data-include="footer"></div>', footer_html)

    # Remove include.js fetch logic (not needed — partials already inlined),
    # but keep a small inline script for the mobile nav toggle to still work in preview.
    preview_nav_script = """
<script>
function setupNavToggle() {
  const toggle = document.getElementById('nav-toggle');
  const links = document.getElementById('nav-links');
  if (!toggle || !links) return;
  toggle.addEventListener('click', () => {
    links.classList.toggle('open');
    toggle.classList.toggle('open');
    document.body.classList.toggle('nav-open');
  });
  links.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      links.classList.remove('open');
      toggle.classList.remove('open');
      document.body.classList.remove('nav-open');
    });
  });
}
document.addEventListener('DOMContentLoaded', setupNavToggle);
</script>
"""
    html = re.sub(
        r'\s*<script src="assets/js/include\.js"></script>\s*',
        preview_nav_script,
        html
    )

    # Inline images as base64 (preview only)
    html = inline_images(html)

    (PREVIEW_DIR / page).write_text(html)
    print(f"built preview/{page}")
