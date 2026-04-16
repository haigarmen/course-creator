---
name: export-course
description: Compile all lesson content for a course into a single combined document (.docx or .html), with a generated table of contents and module dividers.
version: "1.1.0"
tags: [export, documentation, publishing, pandoc, docx, html]
repository: https://github.com/haigarmen/course-creator
compatibility: [claude-code, claude]
---

1. Accept inputs:
   - `course_id` — id of the course to export (e.g. `tumo2026`)
   - `output_format` — `docx` (default) or `html`
   - `course_path` — path to the course directory (default: `courses/<course_id>/`)

2. Read `course.yml` to extract the course title, subtitle, description, estimated hours, and tags.

3. Collect and sort all modules by scanning `course_path/modules/` for directories containing a `module.yml`. Read each `module.yml` to get the module title, description, and order. Sort by the `order` field.

4. For each module in order, collect and sort all lessons by scanning the module's `lessons/` subdirectory for directories containing a `lesson.md`. Read each `lesson.md` frontmatter to get the lesson title and order. Sort by the `order` field.

5. Build the combined document content in this order:

   **Cover section:**
   - Course title (H1)
   - Subtitle and date on separate lines
   - A horizontal rule
   - Course overview table: duration, disciplines, tools, format, final output — drawn from `course.yml` fields

   **For each module:**
   - A module divider (H2): `## Module N — <title>`
   - The module description paragraph
   - A horizontal rule

   **For each lesson in the module:**
   - The lesson heading (H1): `# <lesson title>`
   - The full lesson body content with one transformation: any fenced Mermaid code blocks (` ```mermaid ... ``` `) replaced with a readable text-based equivalent:
     - If the diagram is a flowchart, render it as a `>` blockquote signal flow description (e.g. `> **A** → **B** → **C**`)
     - If the diagram contains a table-like structure (families, comparisons), render it as a markdown table instead
     - Preserve all other content (code blocks in other languages, callouts, lists) verbatim

   **Closing line:**
   - `*End of course handbook. <course title>.*`

6. Write the combined content to `/tmp/<course_id>-combined.md`.

7. Attempt to export using pandoc:
   ```
   pandoc /tmp/<course_id>-combined.md --toc --toc-depth=2 -o <course_path>/<course_id>-course-document.docx
   ```
   - If pandoc succeeds, report the output path and file size.
   - If pandoc is not installed or returns a non-zero exit code, fall back to step 8.

8. HTML export (if pandoc unavailable or `output_format` is `html`):

   **8a. Generate via pandoc then post-process (preferred):**
   - Run pandoc with `--standalone --toc --toc-depth=2 --highlight-style=pygments` targeting a `.html` output file
   - Pandoc HTML-escapes content inside code blocks (e.g. `-->` becomes `--&gt;`, `"` becomes `&quot;`) and wraps Mermaid blocks as `<pre class="mermaid"><code>...</code></pre>`. This breaks Mermaid.js. Fix it with a post-processing step:
     1. Find every `<pre class="mermaid"><code>(.*?)</code></pre>` block (using dotall/multiline matching)
     2. Strip the inner `<code>` / `</code>` tags
     3. Unescape all HTML entities in the block content (convert `&quot;` → `"`, `--&gt;` → `-->`, `&#39;` → `'`, `&amp;` → `&`, etc.)
     4. Write back as `<pre class="mermaid">raw mermaid content</pre>`
   - Inject before `</head>`: Inter + JetBrains Mono from Google Fonts; the CSS block from step 8b; the Mermaid.js script tag with `mermaid.initialize({ startOnLoad: true, theme: 'neutral' })`

   **8b. CSS to inject (embed verbatim in `<style>`):**
   ```css
   body { font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1.7; color: #1a1a1a; max-width: 860px; margin: 0 auto; padding: 2rem 2rem 4rem; }
   h1 { font-size: 2rem; margin-top: 3rem; border-bottom: 2px solid #e5e5e5; padding-bottom: 0.4rem; }
   h2 { font-size: 1.4rem; margin-top: 2.5rem; color: #2a2a2a; }
   h3 { font-size: 1.1rem; margin-top: 2rem; color: #444; }
   pre, code { font-family: 'JetBrains Mono', monospace; font-size: 0.875rem; }
   pre:not(.mermaid) { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px; padding: 1rem 1.2rem; overflow-x: auto; }
   code { background: #f0f0f0; padding: 0.15em 0.35em; border-radius: 3px; }
   pre code { background: none; padding: 0; }
   pre.mermaid { background: #fff; border: 1px solid #e5e5e5; border-radius: 8px; padding: 1.5rem; text-align: center; }
   blockquote { border-left: 4px solid #0070f3; margin: 1.5rem 0; padding: 0.8rem 1.2rem; background: #f0f6ff; border-radius: 0 6px 6px 0; color: #333; }
   table { border-collapse: collapse; width: 100%; margin: 1.5rem 0; font-size: 0.9rem; }
   th { background: #f6f8fa; font-weight: 600; }
   th, td { border: 1px solid #d0d7de; padding: 0.6rem 0.9rem; text-align: left; }
   tr:nth-child(even) td { background: #fafafa; }
   hr { border: none; border-top: 1px solid #e5e5e5; margin: 2.5rem 0; }
   nav#TOC { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 8px; padding: 1.5rem 2rem; margin: 2rem 0 3rem; }
   nav#TOC ul { margin: 0.3rem 0; padding-left: 1.4rem; }
   nav#TOC li { margin: 0.25rem 0; }
   nav#TOC a { color: #0070f3; text-decoration: none; }
   a { color: #0070f3; }
   @media print {
     body { max-width: 100%; padding: 0; font-size: 11pt; }
     h1 { page-break-before: always; }
     h1:first-of-type { page-break-before: avoid; }
     pre.mermaid { page-break-inside: avoid; }
     nav#TOC { page-break-after: always; }
   }
   ```

   **8c. Direct Python fallback (if pandoc unavailable):**
   - Write the HTML file directly without pandoc, embedding the combined markdown content converted to minimal HTML (headings, paragraphs, code blocks, blockquotes). Preserve Mermaid fenced blocks as `<pre class="mermaid">raw content</pre>` — do NOT HTML-escape the Mermaid block contents.
   - Apply the same CSS from step 8b and the same Mermaid.js script tag.

9. Return the output file path and a one-line summary of what was produced (format, number of modules, number of lessons).
