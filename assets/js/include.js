// ============================================
// include.js — Loads partials (nav / footer) into placeholders
//
// How it works: finds every element with a data-include="xxx"
// attribute, fetches /partials/xxx.html, and injects the content
// into that element.
//
// Each page only needs to write:
//   <div data-include="nav"></div>
//   <div data-include="footer"></div>
// No need to hand-write the nav/footer markup repeatedly.
//
// Note: fetch() only works over http/https (opening the html file
// directly via file:// will throw a CORS error). This works fine
// once deployed to Cloudflare Pages / GitHub Pages. For local
// preview, run a local server with `python3 -m http.server`.
// ============================================

async function loadPartial(el) {
  const name = el.getAttribute('data-include');
  try {
    const res = await fetch(`partials/${name}.html`);
    if (!res.ok) throw new Error(`Failed to load partial: ${name}`);
    const html = await res.text();
    el.outerHTML = html;
  } catch (err) {
    console.error(err);
    el.innerHTML = `<!-- failed to load ${name} -->`;
  }
}

function highlightActiveNav() {
  const path = window.location.pathname.split('/').pop().replace('.html', '') || 'index';
  document.querySelectorAll('[data-nav]').forEach(link => {
    if (link.getAttribute('data-nav') === path) {
      link.classList.add('active');
    }
  });
}

function setupNavToggle() {
  const toggle = document.getElementById('nav-toggle');
  const links = document.getElementById('nav-links');
  if (!toggle || !links) return;

  toggle.addEventListener('click', () => {
    links.classList.toggle('open');
    toggle.classList.toggle('open');
    document.body.classList.toggle('nav-open');
  });

  // Close the menu automatically after tapping a link
  links.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      links.classList.remove('open');
      toggle.classList.remove('open');
      document.body.classList.remove('nav-open');
    });
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  const includes = document.querySelectorAll('[data-include]');
  await Promise.all(Array.from(includes).map(loadPartial));
  highlightActiveNav();
  setupNavToggle();
});
