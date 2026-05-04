"""Static site generator — assembles components into a single HTML file."""

from pathlib import Path
from models import Person
from components import (
    NavBar,
    HeroSection,
    AboutSection,
    SkillsSection,
    ProjectsSection,
    TimelineSection,
    ContactSection,
    Footer,
)
from styles import build_css


SCRIPTS = """
<script>
// Scroll spy — animate progress bars and reveal elements on scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add('visible');
    // Animate progress bars inside revealed sections
    entry.target.querySelectorAll('.progress-fill').forEach(bar => {
      bar.style.width = bar.dataset.value + '%';
    });
  });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal, .section, section').forEach(el => observer.observe(el));

// Trigger progress bars already in view on load
window.addEventListener('load', () => {
  document.querySelectorAll('.progress-fill').forEach(bar => {
    const rect = bar.closest('section')?.getBoundingClientRect();
    if (rect && rect.top < window.innerHeight) {
      bar.style.width = bar.dataset.value + '%';
    }
  });
});

// Mobile nav toggle
document.getElementById('navToggle')?.addEventListener('click', () => {
  document.querySelector('.nav__links')?.classList.toggle('open');
});

// Smooth active link highlight on scroll
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav__link');
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY + 80;
  sections.forEach(sec => {
    if (scrollY >= sec.offsetTop && scrollY < sec.offsetTop + sec.offsetHeight) {
      navLinks.forEach(l => l.classList.remove('nav__link--active'));
      const active = document.querySelector(`.nav__link[href="#${sec.id}"]`);
      active?.classList.add('nav__link--active');
    }
  });
}, { passive: true });
</script>
"""


def build_page(person: Person) -> str:
    """Assemble all components into a complete HTML document."""
    css = build_css()

    nav = NavBar(person.name).render()
    hero = HeroSection(person).render()
    about = AboutSection(person).render()
    skills = SkillsSection(person.skills).render()
    projects = ProjectsSection(person.projects).render()
    timeline = TimelineSection(person.timeline).render()
    contact = ContactSection(person).render()
    footer = Footer(person.name).render()

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{person.name} — Portfolio</title>
  <meta name="description" content="{person.tagline}">
  <style>{css}</style>
</head>
<body>
  {nav}
  <main>
    {hero}
    {about}
    {skills}
    {projects}
    {timeline}
    {contact}
  </main>
  {footer}
  {SCRIPTS}
</body>
</html>"""


def generate(person: Person, output_path: Path) -> None:
    """Write the portfolio HTML to disk."""
    html = build_page(person)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    size_kb = len(html.encode()) / 1024
    print(f"Generated: {output_path}  ({size_kb:.1f} KB)")
