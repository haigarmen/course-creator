#!/usr/bin/env python3
"""
Generic course document builder for the course-creator system.

Reads course structure from course.yml / module.yml / lesson.md frontmatter.
Produces three export artifacts for any course:
  <course-id>-combined.md           (Stage A — assembled markdown)
  <course-id>-course-document.html  (Stage B — styled HTML)
  <course-id>-course-document.docx  (Stage C — Word document via pandoc)

Usage:
  python3 build_course_html.py <path/to/course>

Example:
  python3 build_course_html.py ../../courses/tumo2026
  python3 build_course_html.py ../../courses/guitar-pedal-course-2
"""

import os, re, sys, subprocess, tempfile, html as htmllib
from datetime import date

# ── Lightweight YAML field extraction (no PyYAML dependency) ─────────────────

def yml_str(text, key, default=''):
    m = re.search(rf'^{re.escape(key)}:\s*"([^"]*)"', text, re.MULTILINE)
    if m:
        return m.group(1)
    m = re.search(rf'^{re.escape(key)}:\s*([^"\n#][^\n]*?)(?:\s*#.*)?$', text, re.MULTILINE)
    return m.group(1).strip() if m else default

def yml_int(text, key, default=0):
    m = re.search(rf'^{re.escape(key)}:\s*(\d+)', text, re.MULTILINE)
    return int(m.group(1)) if m else default

def yml_list(text, key):
    # Inline: key: ["a", "b"]
    m = re.search(rf'^{re.escape(key)}:\s*\[([^\]]*)\]', text, re.MULTILINE)
    if m:
        return [s.strip().strip('"\'') for s in m.group(1).split(',') if s.strip().strip('"\'')]
    # Block: key:\n  - "a"\n  - "b"
    m = re.search(rf'^{re.escape(key)}:\s*\n((?:[ \t]+-[^\n]+\n?)+)', text, re.MULTILINE)
    if m:
        return [re.sub(r'^\s*-\s*"?|"?\s*$', '', ln).strip()
                for ln in m.group(1).splitlines() if ln.strip().startswith('-')]
    return []

def read_frontmatter(text):
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            return text[3:end]
    return ''

def strip_frontmatter(text):
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            return text[end+4:].lstrip('\n')
    return text

# ── Course structure reader ───────────────────────────────────────────────────

def read_course(course_path):
    yml_path = os.path.join(course_path, 'course.yml')
    with open(yml_path, encoding='utf-8') as f:
        yml = f.read()

    course = {
        'id':          yml_str(yml, 'id'),
        'title':       yml_str(yml, 'title'),
        'lab_title':   yml_str(yml, 'lab_title'),
        'subtitle':    yml_str(yml, 'subtitle'),
        'byline':      yml_str(yml, 'byline'),
        'description': yml_str(yml, 'description'),
        'version':     yml_str(yml, 'version', '1.0.0'),
        'hours':       yml_int(yml, 'estimated_hours', 0),
        'tags':        yml_list(yml, 'tags'),
        'prereqs':     yml_list(yml, 'prerequisites'),
        'accent':      yml_str(yml, 'accent', '#e05a00'),
        'accent2':     yml_str(yml, 'accent2', '#5a00e0'),
        'path':        course_path,
    }

    mods_root = os.path.join(course_path, 'modules')
    mod_dirs = sorted([
        d for d in os.listdir(mods_root)
        if os.path.isdir(os.path.join(mods_root, d)) and not d.startswith('.')
    ])

    global_day = 0
    modules = []
    for mod_dir in mod_dirs:
        mod_path  = os.path.join(mods_root, mod_dir)
        mod_yml_p = os.path.join(mod_path, 'module.yml')
        if not os.path.exists(mod_yml_p):
            continue
        with open(mod_yml_p, encoding='utf-8') as f:
            mod_yml = f.read()

        les_root = os.path.join(mod_path, 'lessons')
        if not os.path.isdir(les_root):
            continue
        les_dirs = sorted([
            d for d in os.listdir(les_root)
            if os.path.isdir(os.path.join(les_root, d)) and not d.startswith('.')
        ])

        lessons = []
        for les_dir in les_dirs:
            les_path = os.path.join(les_root, les_dir, 'lesson.md')
            if not os.path.exists(les_path):
                continue
            with open(les_path, encoding='utf-8') as f:
                les_text = f.read()
            front = read_frontmatter(les_text)
            global_day += 1
            lessons.append({
                'path':  les_path,
                'slug':  les_dir,
                'title': yml_str(front, 'title'),
                'order': yml_int(front, 'order', 0),
                'type':  yml_str(front, 'type', 'interactive'),
                'mins':  yml_int(front, 'estimated_minutes', 60),
                'day':   global_day,
            })
        lessons.sort(key=lambda l: l['order'])

        modules.append({
            'id':    mod_dir,
            'num':   yml_int(mod_yml, 'order', len(modules) + 1),
            'title': yml_str(mod_yml, 'title'),
            'desc':  yml_str(mod_yml, 'description'),
            'venue': yml_str(mod_yml, 'venue'),
            'lessons': lessons,
        })
    modules.sort(key=lambda m: m['num'])
    course['modules'] = modules
    return course

# ── HTML helpers ──────────────────────────────────────────────────────────────

def preprocess_md(md_text):
    return re.sub(r'(\*\*[^*]+\*\*:?)\n([-*])', r'\1\n\n\2', md_text)

def md_to_html(md_text):
    md_text = preprocess_md(md_text)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(md_text)
        tmp = f.name
    result = subprocess.run(
        ['pandoc', tmp, '--from', 'markdown', '--to', 'html', '--highlight-style=pygments'],
        capture_output=True, text=True
    )
    os.unlink(tmp)
    return result.stdout

def fix_mermaid(html):
    def replacer(m):
        inner = m.group(1)
        for old, new in [('&quot;','"'),('--&gt;','-->'),('&#39;',"'"),('&amp;','&'),('&lt;','<'),('&gt;','>')]:
            inner = inner.replace(old, new)
        inner = re.sub(r'^<code[^>]*>', '', inner.strip())
        inner = re.sub(r'</code>$', '', inner.strip())
        return f'<div class="mermaid">{inner}</div>'
    html = re.sub(r'<pre class="mermaid"><code>(.*?)</code></pre>', replacer, html, flags=re.DOTALL)
    html = re.sub(r'<pre class="mermaid">(.*?)</pre>',
                  lambda m: f'<div class="mermaid">{m.group(1)}</div>', html, flags=re.DOTALL)
    return html

def transform_session_headings(html):
    def replacer(m):
        return (
            f'<div class="time-block">'
            f'<div class="time-stamp">{htmllib.escape(m.group(1).strip())}</div>'
            f'<div class="time-content"><strong>{htmllib.escape(m.group(2).strip())}</strong>'
        )
    html = re.sub(
        r'<h3[^>]*>(\d+:\d+\s*[–\-—]+\s*\d+:\d+)\s*[–\-—]+\s*([^<]+)</h3>',
        replacer, html
    )
    parts = re.split(r'(?=<div class="time-block">)', html)
    closed = []
    for i, part in enumerate(parts):
        if i > 0 and part.startswith('<div class="time-block">'):
            closed.append('</div></div>\n')
        closed.append(part)
    if len(parts) > 1:
        closed.append('</div></div>\n')
    return ''.join(closed)

def process_lesson_html(raw_html):
    html = fix_mermaid(raw_html)
    html = html.replace('<input type="checkbox" disabled="" />', '<input type="checkbox" disabled>')
    html = html.replace('<input type="checkbox" disabled="" checked="checked" />', '<input type="checkbox" disabled checked>')

    sections = re.split(r'(<h2[^>]*>.*?</h2>)', html, flags=re.DOTALL)
    out = []
    i = 0
    while i < len(sections):
        chunk = sections[i]
        h2 = re.match(r'<h2[^>]*>(.*?)</h2>', chunk, re.DOTALL)
        if h2:
            heading = re.sub(r'<[^>]+>', '', h2.group(1)).strip()
            body = sections[i+1] if i+1 < len(sections) else ''
            i += 2
            slug = heading.lower()
            if 'learning objective' in slug:
                out.append(f'<div class="objectives"><h4>Learning Objectives</h4>{body}</div>\n')
            elif 'key takeaway' in slug:
                out.append(f'<div class="takeaways"><h4>Key Takeaways</h4>{body}</div>\n')
            elif slug == 'environment':
                out.append(f'<div class="env-box">{body}</div>\n')
            elif slug == 'materials':
                out.append(f'<div class="materials-box"><h4>Materials</h4>{body}</div>\n')
            elif slug == 'session plan':
                out.append(f'<div class="session-plan"><h2>Session Plan</h2>{transform_session_headings(body)}</div>\n')
            elif slug == 'next steps':
                out.append(f'<div class="next-steps"><h4>Next Steps</h4>{body}</div>\n')
            elif slug == 'overview':
                out.append(f'<div class="lesson-overview">{body}</div>\n')
            else:
                out.append(f'<h2>{heading}</h2>\n{body}')
        else:
            out.append(chunk)
            i += 1
    return ''.join(out)

def lesson_badge(lesson):
    t = lesson['type']
    if t == 'reading':
        return 'Reading'
    if t in ('hands-on', 'project'):
        return 'Hands-On'
    return f'Day {lesson["day"]}'  # interactive / default

def lesson_duration(mins):
    if mins < 60:
        return f'{mins} min'
    h = mins // 60
    return f'{h} hr' + ('s' if h > 1 else '')

# ── CSS (accent and accent2 injected at build time) ───────────────────────────

CSS_TEMPLATE = """
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --black:   #0f0f0f;
    --ink:     #1a1a1a;
    --mid:     #555;
    --light:   #888;
    --rule:    #ddd;
    --bg-alt:  #f7f7f7;
    --accent:  {accent};
    --accent2: {accent2};
    --green:   #00875a;
    --page-w:  740px;
  }}

  html {{ font-size: 15px; }}
  body {{ font-family: 'Inter', system-ui, sans-serif; color: var(--ink); line-height: 1.65; background: #fff; max-width: var(--page-w); margin: 0 auto; padding: 0 2rem 4rem; }}

  .cover {{ min-height: 100vh; display: flex; flex-direction: column; justify-content: center; padding: 4rem 0 6rem; border-bottom: 3px solid var(--black); margin-bottom: 3rem; page-break-after: always; }}
  .cover-label {{ font-size: 0.75rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: var(--accent); margin-bottom: 1.5rem; }}
  .cover-byline {{ font-size: 0.95rem; color: var(--mid); margin-top: -1rem; margin-bottom: 2rem; }}
  .cover h1 {{ font-size: 3rem; font-weight: 700; line-height: 1.1; color: var(--black); margin-bottom: 1.5rem; }}
  .cover .subtitle {{ font-size: 1.15rem; color: var(--mid); max-width: 520px; margin-bottom: 3rem; line-height: 1.6; }}
  .cover-meta {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; border-top: 1px solid var(--rule); padding-top: 2rem; }}
  .cover-meta-item .label {{ font-size: 0.7rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--light); display: block; margin-bottom: 0.25rem; }}
  .cover-meta-item .value {{ font-weight: 600; font-size: 0.95rem; color: var(--ink); }}

  .toc {{ margin-bottom: 3rem; page-break-after: always; }}
  .toc h2 {{ margin-bottom: 1.5rem; }}
  .toc ol {{ list-style: none; }}
  .toc > ol > li {{ border-bottom: 1px dotted var(--rule); padding: 0.5rem 0; }}
  .toc-module {{ font-weight: 600; color: var(--ink); font-size: 0.95rem; }}
  .toc-venue {{ font-size: 0.78rem; color: var(--accent); font-weight: 500; margin-left: 0.5em; }}
  .toc-lessons {{ list-style: none; margin-left: 1.5rem; margin-top: 0.2rem; }}
  .toc-lessons li {{ color: var(--mid); font-size: 0.88rem; padding: 0.15rem 0; }}
  .toc-lessons li .badge {{ color: var(--accent); font-weight: 500; font-size: 0.78rem; margin-right: 0.4em; }}

  h1 {{ font-size: 2rem; font-weight: 700; line-height: 1.15; color: var(--black); margin-bottom: 0.75rem; }}
  h2 {{ font-size: 1.35rem; font-weight: 600; color: var(--black); margin: 2rem 0 0.75rem; padding-bottom: 0.4rem; border-bottom: 2px solid var(--rule); }}
  h3 {{ font-size: 1rem; font-weight: 600; color: var(--ink); margin: 1.5rem 0 0.4rem; }}
  h4 {{ font-size: 0.9rem; font-weight: 600; color: var(--mid); margin: 1rem 0 0.3rem; text-transform: uppercase; letter-spacing: 0.05em; }}
  p {{ margin-bottom: 0.8rem; }}
  em {{ font-style: italic; }}
  strong {{ font-weight: 600; }}
  ul, ol {{ margin: 0.5rem 0 0.8rem 1.4rem; }}
  li {{ margin-bottom: 0.3rem; }}
  li::marker {{ color: var(--accent); }}
  a {{ color: var(--accent2); text-decoration: none; }}
  hr {{ border: none; border-top: 1px solid var(--rule); margin: 2rem 0; }}

  code {{ font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; background: var(--bg-alt); padding: 0.1em 0.35em; border-radius: 3px; color: var(--accent2); }}
  pre {{ background: #1a1a2e; color: #e8e8f0; padding: 1.1rem 1.2rem; border-radius: 6px; overflow-x: auto; margin: 0.8rem 0 1rem; font-size: 0.82rem; line-height: 1.55; }}
  pre code {{ background: none; color: inherit; padding: 0; font-size: inherit; }}

  blockquote {{ border-left: 3px solid var(--accent); background: #fff8f4; padding: 0.8rem 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0; font-size: 0.92rem; }}
  blockquote strong {{ color: var(--accent); }}

  table {{ width: 100%; border-collapse: collapse; margin: 0.8rem 0 1rem; font-size: 0.88rem; }}
  th {{ background: var(--black); color: #fff; font-weight: 600; text-align: left; padding: 0.5rem 0.75rem; font-size: 0.8rem; letter-spacing: 0.04em; }}
  td {{ padding: 0.45rem 0.75rem; border-bottom: 1px solid var(--rule); vertical-align: top; }}
  tr:nth-child(even) td {{ background: var(--bg-alt); }}

  .mermaid {{ background: var(--bg-alt); border: 1px solid var(--rule); border-radius: 6px; padding: 1rem; margin: 0.8rem 0 1rem; text-align: center; }}

  .module-header {{ background: var(--black); color: #fff; padding: 2rem 2rem 1.5rem; margin: 3rem -2rem 2rem; page-break-before: always; }}
  .module-header .module-number {{ font-size: 0.72rem; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: var(--accent); display: block; margin-bottom: 0.5rem; }}
  .module-header h2 {{ font-size: 1.6rem; color: #fff; border: none; margin: 0 0 0.3rem; padding: 0; }}
  .module-header .module-venue {{ font-size: 0.8rem; color: var(--accent); font-weight: 500; margin-bottom: 0.5rem; }}
  .module-header .module-desc {{ color: #aaa; font-size: 0.92rem; max-width: 560px; margin: 0; }}

  .lesson-header {{ margin: 2.5rem 0 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid var(--rule); }}
  .lesson-header .lesson-badge {{ display: inline-block; background: var(--accent); color: #fff; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; padding: 0.2em 0.6em; border-radius: 3px; margin-bottom: 0.5rem; }}
  .lesson-header h3 {{ font-size: 1.4rem; font-weight: 700; color: var(--black); margin: 0 0 0.4rem; }}
  .lesson-meta {{ display: flex; gap: 1.5rem; font-size: 0.8rem; color: var(--light); }}

  .lesson-overview {{ font-size: 0.95rem; color: var(--mid); margin-bottom: 1.5rem; line-height: 1.7; border-left: 3px solid var(--rule); padding-left: 1rem; }}
  .lesson-overview p {{ margin-bottom: 0; }}

  .objectives {{ background: #f0f4ff; border: 1px solid #c0cff7; border-radius: 6px; padding: 1rem 1.2rem; margin: 1rem 0; }}
  .objectives h4 {{ color: var(--accent2); margin-top: 0; }}
  .objectives ul {{ margin-bottom: 0; }}
  .objectives li {{ font-size: 0.9rem; }}
  .objectives input[type="checkbox"] {{ accent-color: var(--accent2); margin-right: 0.4em; }}

  .env-box {{ background: #f4fef4; border: 1px solid #b6e0b6; border-left: 3px solid var(--green); border-radius: 0 6px 6px 0; padding: 0.8rem 1.1rem; margin: 0.8rem 0; font-size: 0.88rem; }}
  .env-box p:last-child {{ margin-bottom: 0; }}
  .env-box::before {{ content: "Environment"; display: block; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--green); margin-bottom: 0.4rem; }}

  .materials-box {{ background: #fffbf0; border: 1px solid #e8d89e; border-radius: 6px; padding: 0.8rem 1.2rem; margin: 0.8rem 0; font-size: 0.88rem; }}
  .materials-box h4 {{ color: #8a6000; margin-top: 0; }}
  .materials-box p:last-child, .materials-box ul:last-child {{ margin-bottom: 0; }}

  .takeaways {{ background: var(--black); color: #fff; padding: 1rem 1.3rem; border-radius: 6px; margin: 1.5rem 0 0.5rem; }}
  .takeaways h4 {{ color: var(--accent); margin-top: 0; }}
  .takeaways li {{ color: #ddd; font-size: 0.88rem; margin-bottom: 0.4rem; }}
  .takeaways li::marker {{ color: var(--accent); }}
  .takeaways strong {{ color: #fff; }}

  .next-steps {{ background: var(--bg-alt); border: 1px solid var(--rule); border-radius: 6px; padding: 0.8rem 1.2rem; margin: 1rem 0; font-size: 0.9rem; }}
  .next-steps h4 {{ color: var(--mid); margin-top: 0; }}
  .next-steps p:last-child {{ margin-bottom: 0; }}

  .session-plan h2 {{ font-size: 1.1rem; border-bottom-color: var(--accent); color: var(--accent); }}
  .session-plan h3 {{ font-size: 0.92rem; margin: 1.2rem 0 0.3rem; }}
  .session-plan h4 {{ color: var(--accent2); margin-top: 1.5rem; border-bottom: 1px solid var(--rule); padding-bottom: 0.25rem; text-transform: none; letter-spacing: 0; font-size: 0.95rem; }}

  .time-block {{ display: flex; gap: 1rem; margin: 0.8rem 0; padding: 0.5rem 0; border-top: 1px dotted var(--rule); }}
  .time-stamp {{ font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--accent); font-weight: 600; white-space: nowrap; padding-top: 0.1rem; min-width: 86px; }}
  .time-content {{ flex: 1; }}
  .time-content p:first-child {{ margin-top: 0; }}
  .time-content p:last-child {{ margin-bottom: 0; }}

  input[type="checkbox"] {{ accent-color: var(--accent2); margin-right: 0.4em; }}
  .task-list-item {{ list-style: none; margin-left: -1.4rem; }}

  @media print {{
    body {{ max-width: 100%; padding: 0; font-size: 10.5pt; }}
    .cover {{ min-height: auto; padding: 3rem 2rem 4rem; }}
    .cover h1 {{ font-size: 2.2rem; }}
    .module-header {{ margin: 2rem 0 1.5rem; padding: 1.5rem; page-break-before: always; }}
    pre {{ font-size: 8pt; }}
    .mermaid, blockquote, .takeaways {{ break-inside: avoid; }}
    .lesson-header, h2, h3 {{ break-after: avoid; }}
  }}
"""

# ── Stage A — Assemble combined.md ───────────────────────────────────────────

def build_combined_md(course):
    today = date.today().isoformat()
    tags  = ' · '.join(course['tags']) if course['tags'] else ''
    prereq = course['prereqs'][0] if course['prereqs'] else 'None'

    display_title = course['lab_title'] or course['title']
    sub_line = f"{course['subtitle']}\n" if course['subtitle'] else f"{course['description']}\n"
    byline_line = f"*{course['byline']}*\n\n" if course['byline'] else ''
    parts = [
        f"# {display_title}\n\n",
        sub_line,
        byline_line,
        f"*{course['title']} — Version {course['version']} — Exported: {today}*\n\n---\n\n",
        f"| | |\n|---|---|\n",
        f"| **Version** | {course['version']} |\n",
        f"| **Disciplines** | {tags} |\n",
        f"| **Prerequisites** | {prereq} |\n\n",
    ]
    for mod in course['modules']:
        parts.append(f"---\n\n## Module {mod['num']} — {mod['title']}\n\n")
        if mod['venue']:
            parts.append(f"*{mod['venue']}*\n\n")
        parts.append(f"{mod['desc']}\n\n---\n\n")
        for les in mod['lessons']:
            with open(les['path'], encoding='utf-8') as f:
                raw = f.read()
            parts.append(f"### {les['title']}\n\n")
            parts.append(strip_frontmatter(raw))
            parts.append('\n\n')
    parts.append(f"---\n\n*End of course document. {course['title']}.*\n")
    return ''.join(parts)

# ── Stage B — Build HTML ──────────────────────────────────────────────────────

def build_html(course):
    cid   = course['id']
    title = htmllib.escape(course['title'])
    desc  = htmllib.escape(course['description'])
    tags  = ' · '.join(course['tags'])
    prereq = course['prereqs'][0] if course['prereqs'] else 'None'
    css   = CSS_TEMPLATE.format(accent=course['accent'], accent2=course['accent2'])

    parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="version" content="{htmllib.escape(course['version'])}">
<title>{title} v{htmllib.escape(course['version'])} — Course Document</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{ startOnLoad: true, theme: 'neutral', fontSize: 13 }});</script>
<style>{css}</style>
</head>
<body>
"""]

    # Cover — lab_title (if set) becomes the h1; course title drops to cover-label
    display_title = htmllib.escape(course['lab_title']) if course['lab_title'] else title
    cover_label   = htmllib.escape(course['title']) if course['lab_title'] else 'Course Document'
    subtitle_html = f'\n  <p class="subtitle">{htmllib.escape(course["subtitle"])}</p>' if course['subtitle'] else ''
    byline_html   = f'\n  <p class="cover-byline">{htmllib.escape(course["byline"])}</p>' if course['byline'] else ''
    parts.append(f"""
<div class="cover">
  <div class="cover-label">{cover_label}</div>
  <h1>{display_title}</h1>{subtitle_html}{byline_html}
  <div class="cover-meta">
    <div class="cover-meta-item"><span class="label">Version</span><span class="value">v{htmllib.escape(course['version'])}</span></div>
    <div class="cover-meta-item"><span class="label">Disciplines</span><span class="value">{htmllib.escape(tags)}</span></div>
    <div class="cover-meta-item"><span class="label">Prerequisites</span><span class="value">{htmllib.escape(prereq)}</span></div>
  </div>
</div>
""")

    # TOC
    parts.append('<div class="toc">\n<h2>Contents</h2>\n<ol>\n')
    for mod in course['modules']:
        venue_html = f'<span class="toc-venue">{htmllib.escape(mod["venue"])}</span>' if mod['venue'] else ''
        parts.append(f'  <li>\n    <div class="toc-module">Module {mod["num"]} — {htmllib.escape(mod["title"])}{venue_html}</div>\n')
        parts.append('    <ul class="toc-lessons">\n')
        for les in mod['lessons']:
            badge = lesson_badge(les)
            parts.append(f'      <li><span class="badge">{badge}</span>{htmllib.escape(les["title"])}</li>\n')
        parts.append('    </ul>\n  </li>\n')
    parts.append('</ol>\n</div>\n')

    # Modules and lessons
    for mod in course['modules']:
        venue_div = f'\n  <div class="module-venue">{htmllib.escape(mod["venue"])}</div>' if mod['venue'] else ''
        parts.append(f"""
<div class="module-header">
  <span class="module-number">Module {mod["num"]}</span>
  <h2>{htmllib.escape(mod["title"])}</h2>{venue_div}
  <p class="module-desc">{htmllib.escape(mod["desc"])}</p>
</div>
""")
        for les in mod['lessons']:
            with open(les['path'], encoding='utf-8') as f:
                raw = f.read()
            body_html = process_lesson_html(md_to_html(strip_frontmatter(raw)))
            badge = lesson_badge(les)
            dur   = lesson_duration(les['mins'])
            parts.append(f"""<div class="lesson-header">
  <span class="lesson-badge">{badge}</span>
  <h3>{htmllib.escape(les["title"])}</h3>
  <div class="lesson-meta"><span>⏱ {dur}</span><span>Module {mod["num"]}</span></div>
</div>
""")
            parts.append(body_html)
            parts.append('\n')

    parts.append(f"""
<hr>
<p style="text-align:center; color: var(--light); font-size: 0.82rem; margin-top: 3rem;">
  <em>End of course document. {title}.</em>
</p>
</body>
</html>
""")
    return ''.join(parts)

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    course_path = os.path.abspath(sys.argv[1])
    if not os.path.isdir(course_path):
        print(f"Error: {course_path} is not a directory")
        sys.exit(1)

    print(f"Reading course from: {course_path}")
    course = read_course(course_path)
    cid = course['id']
    print(f"Course: {course['title']}  v{course['version']}  ({len(course['modules'])} modules, "
          f"{sum(len(m['lessons']) for m in course['modules'])} lessons)")

    # Stage A — combined.md
    combined_md   = os.path.join(course_path, f'{cid}-combined.md')
    combined_text = build_combined_md(course)
    with open(combined_md, 'w', encoding='utf-8') as f:
        f.write(combined_text)
    print(f"\n[Stage A] {combined_md}  ({os.path.getsize(combined_md):,} bytes)")

    # Stage B — HTML
    html_path = os.path.join(course_path, f'{cid}-course-document.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(build_html(course))
    print(f"[Stage B] {html_path}  ({os.path.getsize(html_path):,} bytes)")

    # Stage C — docx
    docx_path = os.path.join(course_path, f'{cid}-course-document.docx')
    result = subprocess.run(
        ['pandoc', combined_md, '--from', 'markdown', '--to', 'docx',
         '--highlight-style', 'pygments', '-o', docx_path],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"[Stage C] {docx_path}  ({os.path.getsize(docx_path):,} bytes)")
    else:
        print(f"[Stage C] ERROR: {result.stderr.strip()}")
        print("          Install pandoc with: brew install pandoc")
