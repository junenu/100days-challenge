"""CSS styles for the portfolio site.

Returns a single string of minification-friendly CSS.
Split into logical sections for readability.
"""


def build_css() -> str:
    sections = [
        _reset_and_variables(),
        _layout(),
        _navbar(),
        _hero(),
        _section_common(),
        _about(),
        _skills(),
        _projects(),
        _timeline(),
        _contact(),
        _footer(),
        _animations(),
        _responsive(),
    ]
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# CSS sections
# ---------------------------------------------------------------------------

def _reset_and_variables() -> str:
    return """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #0d0d14;
  --bg-alt: #12121e;
  --surface: #1a1a2e;
  --surface-hover: #222238;
  --border: #2a2a44;
  --accent: #7c3aed;
  --accent-light: #a78bfa;
  --accent2: #06b6d4;
  --text: #e2e8f0;
  --text-muted: #94a3b8;
  --text-faint: #475569;
  --radius: 12px;
  --radius-sm: 6px;
  --shadow: 0 4px 24px rgba(0,0,0,.4);
  --transition: .25s ease;
  --font: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}

html { scroll-behavior: smooth; font-size: 16px; }
body { background: var(--bg); color: var(--text); font-family: var(--font); line-height: 1.7; }
a { color: var(--accent-light); text-decoration: none; transition: color var(--transition); }
a:hover { color: #fff; }
img { display: block; max-width: 100%; }
"""


def _layout() -> str:
    return """
.container { max-width: 1100px; margin: 0 auto; padding: 0 2rem; }
"""


def _navbar() -> str:
    return """
.nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: .9rem 2rem;
  background: rgba(13,13,20,.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  transition: background var(--transition);
}
.nav__brand { font-size: 1.1rem; font-weight: 700; color: var(--accent-light); letter-spacing: .5px; }
.nav__links { display: flex; gap: 1.8rem; }
.nav__link { color: var(--text-muted); font-size: .9rem; font-weight: 500; position: relative; }
.nav__link::after {
  content: ''; position: absolute; bottom: -2px; left: 0; right: 0;
  height: 2px; background: var(--accent-light);
  transform: scaleX(0); transition: transform var(--transition);
}
.nav__link:hover { color: var(--text); }
.nav__link:hover::after { transform: scaleX(1); }
.nav__toggle { display: none; background: none; border: none; color: var(--text); font-size: 1.4rem; cursor: pointer; }
"""


def _hero() -> str:
    return """
.hero {
  min-height: 100vh; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; padding: 6rem 2rem 4rem;
  background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(124,58,237,.18) 0%, transparent 70%);
  position: relative;
}
.hero__avatar {
  width: 100px; height: 100px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; font-weight: 800; color: #fff;
  margin: 0 auto 1.5rem;
  box-shadow: 0 0 40px rgba(124,58,237,.4);
  animation: pulse-glow 3s ease-in-out infinite;
}
.hero__greeting { color: var(--accent-light); font-size: 1rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: .4rem; }
.hero__name { font-size: clamp(2.4rem, 6vw, 4.5rem); font-weight: 800; letter-spacing: -1px; line-height: 1.1; margin-bottom: .6rem; }
.hero__title { font-size: 1.2rem; color: var(--accent2); font-weight: 500; margin-bottom: 1.2rem; }
.hero__tagline { font-size: 1rem; color: var(--text-muted); font-style: italic; max-width: 600px; margin: 0 auto 2rem; }
.hero__social { display: flex; gap: .8rem; justify-content: center; margin-bottom: 2.2rem; }
.social-link {
  width: 42px; height: 42px; border-radius: 50%; border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: .75rem; font-weight: 700; color: var(--text-muted);
  transition: all var(--transition);
}
.social-link:hover { border-color: var(--accent-light); color: var(--accent-light); transform: translateY(-3px); }
.hero__cta { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
.hero__scroll-hint {
  position: absolute; bottom: 2rem; left: 50%;
  transform: translateX(-50%); color: var(--text-faint);
  font-size: .8rem; letter-spacing: 2px; animation: bounce 2s infinite;
}

/* Buttons */
.btn {
  display: inline-block; padding: .75rem 1.8rem; border-radius: 50px;
  font-weight: 600; font-size: .95rem; transition: all var(--transition); cursor: pointer; border: none;
}
.btn--primary {
  background: linear-gradient(135deg, var(--accent), #5b21b6);
  color: #fff; box-shadow: 0 4px 20px rgba(124,58,237,.4);
}
.btn--primary:hover { transform: translateY(-2px); box-shadow: 0 6px 28px rgba(124,58,237,.6); color: #fff; }
.btn--outline { border: 1.5px solid var(--accent-light); color: var(--accent-light); }
.btn--outline:hover { background: rgba(124,58,237,.15); transform: translateY(-2px); color: var(--accent-light); }
.btn--lg { padding: 1rem 2.4rem; font-size: 1.05rem; }
"""


def _section_common() -> str:
    return """
.section { padding: 6rem 0; }
.section--alt { background: var(--bg-alt); }
.section-header { text-align: center; margin-bottom: 3.5rem; }
.section-title { font-size: 2.2rem; font-weight: 800; position: relative; display: inline-block; }
.section-title::after {
  content: ''; display: block; width: 48px; height: 4px; border-radius: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  margin: .6rem auto 0;
}
.section-subtitle { color: var(--text-muted); margin-top: .6rem; font-size: 1rem; }
"""


def _about() -> str:
    return """
.about__grid { display: grid; grid-template-columns: 1fr 280px; gap: 3rem; align-items: start; }
.about__text { font-size: 1.05rem; color: var(--text-muted); line-height: 1.9; }
.about__meta {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem;
}
.about__meta-item { display: flex; align-items: center; gap: .8rem; color: var(--text-muted); font-size: .95rem; }
.about__meta-icon { font-size: 1.2rem; }
"""


def _skills() -> str:
    return """
.skills__grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; }
.skill-group {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.8rem;
}
.skill-group__title { font-size: 1rem; font-weight: 700; color: var(--accent-light); margin-bottom: 1.2rem; text-transform: uppercase; letter-spacing: 1px; }
.progress-item { margin-bottom: 1rem; }
.progress-item:last-child { margin-bottom: 0; }
.progress-header { display: flex; justify-content: space-between; margin-bottom: .4rem; }
.progress-label { font-size: .9rem; font-weight: 500; }
.progress-value { font-size: .85rem; color: var(--text-muted); }
.progress-track { height: 7px; background: var(--border); border-radius: 99px; overflow: hidden; }
.progress-fill {
  height: 100%; border-radius: 99px; width: 0;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  transition: width 1.2s cubic-bezier(.22,.61,.36,1);
}
"""


def _projects() -> str:
    return """
.projects__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.6rem;
  display: flex; gap: 1.2rem; align-items: flex-start;
  transition: all var(--transition);
}
.card:hover { border-color: var(--accent); transform: translateY(-4px); box-shadow: var(--shadow); }
.card--featured { border-color: rgba(124,58,237,.4); background: linear-gradient(135deg, rgba(124,58,237,.05), var(--surface)); }
.card__emoji { font-size: 2rem; flex-shrink: 0; }
.card__body { flex: 1; min-width: 0; }
.card__title-row { display: flex; align-items: center; gap: .6rem; margin-bottom: .5rem; flex-wrap: wrap; }
.card__title { font-size: 1.05rem; font-weight: 700; }
.card__desc { font-size: .88rem; color: var(--text-muted); line-height: 1.6; margin-bottom: .8rem; }
.card__tech { display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: .8rem; }
.card__link { font-size: .85rem; font-weight: 600; color: var(--accent-light); }
.card__link:hover { color: #fff; }

/* Badges */
.badge { display: inline-block; padding: .2rem .65rem; border-radius: 99px; font-size: .75rem; font-weight: 600; }
.badge--default { background: rgba(255,255,255,.07); color: var(--text-muted); }
.badge--tech { background: rgba(6,182,212,.12); color: var(--accent2); border: 1px solid rgba(6,182,212,.25); }
.badge--featured { background: rgba(124,58,237,.2); color: var(--accent-light); border: 1px solid rgba(124,58,237,.4); }
"""


def _timeline() -> str:
    return """
.timeline { position: relative; max-width: 700px; margin: 0 auto; }
.timeline::before {
  content: ''; position: absolute; left: 22px; top: 0; bottom: 0; width: 2px;
  background: linear-gradient(to bottom, var(--accent), var(--accent2));
  border-radius: 1px;
}
.timeline__item { display: flex; gap: 1.5rem; margin-bottom: 2.5rem; animation: fade-in-up .5s both; }
.timeline__dot {
  width: 46px; height: 46px; border-radius: 50%; flex-shrink: 0;
  background: var(--surface); border: 2px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; z-index: 1;
  transition: border-color var(--transition);
}
.timeline__item:hover .timeline__dot { border-color: var(--accent-light); }
.timeline__content {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.3rem 1.5rem;
  flex: 1; transition: border-color var(--transition);
}
.timeline__item:hover .timeline__content { border-color: var(--border); box-shadow: var(--shadow); }
.timeline__year { font-size: .8rem; color: var(--accent-light); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.timeline__title { font-size: 1.05rem; font-weight: 700; margin: .25rem 0 .2rem; }
.timeline__org { font-size: .9rem; color: var(--accent2); margin-bottom: .5rem; }
.timeline__desc { font-size: .88rem; color: var(--text-muted); line-height: 1.6; }
"""


def _contact() -> str:
    return """
.contact {
  background: radial-gradient(ellipse 70% 60% at 50% 100%, rgba(124,58,237,.2) 0%, transparent 70%);
}
.contact__inner { text-align: center; max-width: 560px; margin: 0 auto; }
.contact__title { font-size: 2.2rem; font-weight: 800; margin-bottom: 1rem; }
.contact__text { color: var(--text-muted); font-size: 1.05rem; margin-bottom: 2rem; }
"""


def _footer() -> str:
    return """
.footer {
  padding: 2rem; text-align: center;
  color: var(--text-faint); font-size: .85rem;
  border-top: 1px solid var(--border);
}
"""


def _animations() -> str:
    return """
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 40px rgba(124,58,237,.4); }
  50%       { box-shadow: 0 0 60px rgba(124,58,237,.7); }
}
@keyframes bounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50%       { transform: translateX(-50%) translateY(-8px); }
}
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
.reveal { opacity: 0; transform: translateY(24px); transition: opacity .6s ease, transform .6s ease; }
.reveal.visible { opacity: 1; transform: translateY(0); }
"""


def _responsive() -> str:
    return """
@media (max-width: 768px) {
  .nav__links { display: none; }
  .nav__toggle { display: block; }
  .nav__links.open {
    display: flex; flex-direction: column; gap: 1rem;
    position: fixed; top: 60px; left: 0; right: 0;
    background: var(--bg-alt); padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--border);
  }
  .about__grid { grid-template-columns: 1fr; }
  .hero__name { font-size: 2.4rem; }
  .timeline::before { left: 20px; }
}
@media (max-width: 480px) {
  .projects__grid { grid-template-columns: 1fr; }
  .skills__grid { grid-template-columns: 1fr; }
}
"""
