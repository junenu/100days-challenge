"""Reusable HTML components for the portfolio site.

Each component is a callable class with a render() method.
Components are composable — any component can contain others.
"""

from abc import ABC, abstractmethod
from typing import Optional
from models import Person, Skill, Project, TimelineEntry


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Component(ABC):
    """Base class for all renderable HTML components."""

    @abstractmethod
    def render(self) -> str:
        """Return the HTML string for this component."""

    def __str__(self) -> str:
        return self.render()


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

class Tag(Component):
    """Generic HTML tag wrapper."""

    def __init__(self, tag: str, content: str, cls: str = "", attrs: dict[str, str] | None = None):
        self.tag = tag
        self.content = content
        self.cls = cls
        self.attrs = attrs or {}

    def render(self) -> str:
        attr_str = f' class="{self.cls}"' if self.cls else ""
        for k, v in self.attrs.items():
            attr_str += f' {k}="{v}"'
        return f"<{self.tag}{attr_str}>{self.content}</{self.tag}>"


class Badge(Component):
    """Small pill-shaped label."""

    def __init__(self, text: str, variant: str = "default"):
        self.text = text
        self.variant = variant

    def render(self) -> str:
        return f'<span class="badge badge--{self.variant}">{self.text}</span>'


class ProgressBar(Component):
    """Animated skill level progress bar."""

    def __init__(self, label: str, value: int):
        self.label = label
        self.value = max(0, min(100, value))

    def render(self) -> str:
        return f"""
        <div class="progress-item">
          <div class="progress-header">
            <span class="progress-label">{self.label}</span>
            <span class="progress-value">{self.value}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width:{self.value}%" data-value="{self.value}"></div>
          </div>
        </div>"""


class SectionHeader(Component):
    """Consistent section title + subtitle block."""

    def __init__(self, title: str, subtitle: str = ""):
        self.title = title
        self.subtitle = subtitle

    def render(self) -> str:
        sub = f'<p class="section-subtitle">{self.subtitle}</p>' if self.subtitle else ""
        return f"""
        <div class="section-header">
          <h2 class="section-title">{self.title}</h2>
          {sub}
        </div>"""


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

class NavBar(Component):
    """Fixed top navigation bar."""

    NAV_ITEMS = [
        ("About", "#about"),
        ("Skills", "#skills"),
        ("Projects", "#projects"),
        ("Timeline", "#timeline"),
        ("Contact", "#contact"),
    ]

    def __init__(self, name: str):
        self.name = name

    def render(self) -> str:
        items = "".join(
            f'<a href="{href}" class="nav__link">{label}</a>'
            for label, href in self.NAV_ITEMS
        )
        return f"""
        <nav class="nav" id="navbar">
          <div class="nav__brand">{self.name}</div>
          <div class="nav__links">{items}</div>
          <button class="nav__toggle" id="navToggle" aria-label="menu">☰</button>
        </nav>"""


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

class HeroSection(Component):
    """Full-viewport hero section with avatar and headline."""

    def __init__(self, person: Person):
        self.person = person

    def render(self) -> str:
        p = self.person
        social_links = "".join(
            f'<a href="{s.url}" class="social-link" target="_blank" rel="noopener">{s.icon}</a>'
            for s in p.social_links
        )
        return f"""
        <section class="hero" id="hero">
          <div class="hero__content">
            <div class="hero__avatar">{p.avatar_initials}</div>
            <p class="hero__greeting">Hello, I'm</p>
            <h1 class="hero__name">{p.name}</h1>
            <p class="hero__title">{p.title}</p>
            <p class="hero__tagline">"{p.tagline}"</p>
            <div class="hero__social">{social_links}</div>
            <div class="hero__cta">
              <a href="#projects" class="btn btn--primary">View My Work</a>
              <a href="#contact" class="btn btn--outline">Get In Touch</a>
            </div>
          </div>
          <div class="hero__scroll-hint">↓ scroll</div>
        </section>"""


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------

class AboutSection(Component):
    """Bio and basic info section."""

    def __init__(self, person: Person):
        self.person = person

    def render(self) -> str:
        p = self.person
        header = SectionHeader("About Me", "Who I am and what drives me").render()
        return f"""
        <section class="section" id="about">
          <div class="container">
            {header}
            <div class="about__grid">
              <div class="about__bio">
                <p class="about__text">{p.bio}</p>
              </div>
              <div class="about__meta">
                <div class="about__meta-item">
                  <span class="about__meta-icon">📍</span>
                  <span>{p.location}</span>
                </div>
                <div class="about__meta-item">
                  <span class="about__meta-icon">✉️</span>
                  <a href="mailto:{p.email}">{p.email}</a>
                </div>
              </div>
            </div>
          </div>
        </section>"""


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

class SkillGroup(Component):
    """A group of skill progress bars under a category heading."""

    def __init__(self, category: str, skills: list[Skill]):
        self.category = category
        self.skills = skills

    def render(self) -> str:
        bars = "".join(ProgressBar(s.name, s.level).render() for s in self.skills)
        return f"""
        <div class="skill-group">
          <h3 class="skill-group__title">{self.category}</h3>
          {bars}
        </div>"""


class SkillsSection(Component):
    """Skills section with categorized progress bars."""

    def __init__(self, skills: list[Skill]):
        self.skills = skills

    def _group_by_category(self) -> dict[str, list[Skill]]:
        groups: dict[str, list[Skill]] = {}
        for skill in self.skills:
            groups.setdefault(skill.category, []).append(skill)
        return groups

    def render(self) -> str:
        header = SectionHeader("Skills", "Technologies I work with").render()
        groups = self._group_by_category()
        group_html = "".join(
            SkillGroup(cat, skills).render()
            for cat, skills in groups.items()
        )
        return f"""
        <section class="section section--alt" id="skills">
          <div class="container">
            {header}
            <div class="skills__grid">{group_html}</div>
          </div>
        </section>"""


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class ProjectCard(Component):
    """Single project card."""

    def __init__(self, project: Project):
        self.project = project

    def render(self) -> str:
        p = self.project
        tech_badges = "".join(Badge(t, "tech").render() for t in p.tech)
        featured_badge = Badge("Featured", "featured").render() if p.featured else ""
        link = (
            f'<a href="{p.url}" class="card__link" target="_blank" rel="noopener">View →</a>'
            if p.url else ""
        )
        return f"""
        <div class="card {'card--featured' if p.featured else ''}">
          <div class="card__emoji">{p.image_emoji}</div>
          <div class="card__body">
            <div class="card__title-row">
              <h3 class="card__title">{p.title}</h3>
              {featured_badge}
            </div>
            <p class="card__desc">{p.description}</p>
            <div class="card__tech">{tech_badges}</div>
            {link}
          </div>
        </div>"""


class ProjectsSection(Component):
    """Grid of project cards."""

    def __init__(self, projects: list[Project]):
        self.projects = projects

    def render(self) -> str:
        header = SectionHeader("Projects", "Things I've built").render()
        cards = "".join(ProjectCard(p).render() for p in self.projects)
        return f"""
        <section class="section" id="projects">
          <div class="container">
            {header}
            <div class="projects__grid">{cards}</div>
          </div>
        </section>"""


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------

class TimelineItem(Component):
    """Single entry in the career/education timeline."""

    ICONS = {"work": "💼", "education": "🎓"}

    def __init__(self, entry: TimelineEntry):
        self.entry = entry

    def render(self) -> str:
        e = self.entry
        icon = self.ICONS.get(e.kind, "📌")
        return f"""
        <div class="timeline__item timeline__item--{e.kind}">
          <div class="timeline__dot">{icon}</div>
          <div class="timeline__content">
            <span class="timeline__year">{e.year}</span>
            <h3 class="timeline__title">{e.title}</h3>
            <p class="timeline__org">{e.organization}</p>
            <p class="timeline__desc">{e.description}</p>
          </div>
        </div>"""


class TimelineSection(Component):
    """Vertical timeline of work and education history."""

    def __init__(self, entries: list[TimelineEntry]):
        self.entries = entries

    def render(self) -> str:
        header = SectionHeader("Timeline", "My journey so far").render()
        items = "".join(TimelineItem(e).render() for e in self.entries)
        return f"""
        <section class="section section--alt" id="timeline">
          <div class="container">
            {header}
            <div class="timeline">{items}</div>
          </div>
        </section>"""


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

class ContactSection(Component):
    """Contact CTA section."""

    def __init__(self, person: Person):
        self.person = person

    def render(self) -> str:
        p = self.person
        return f"""
        <section class="section contact" id="contact">
          <div class="container">
            <div class="contact__inner">
              <h2 class="contact__title">Let's Work Together</h2>
              <p class="contact__text">
                新しいプロジェクトや面白いアイデアがあれば、気軽に連絡ください。
              </p>
              <a href="mailto:{p.email}" class="btn btn--primary btn--lg">
                Say Hello ✉️
              </a>
            </div>
          </div>
        </section>"""


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

class Footer(Component):
    """Page footer."""

    def __init__(self, name: str):
        self.name = name

    def render(self) -> str:
        return f"""
        <footer class="footer">
          <p>© 2025 {self.name} · Built with Python</p>
        </footer>"""
