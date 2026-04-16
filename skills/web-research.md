---
name: web-research
description: Search the web for information on a given topic and return a structured summary of findings with sources.
version: "1.0.0"
tags: [research, web, search, content-authoring]
repository: https://github.com/haigarmen/course-creator
compatibility: [claude-code, claude]
---

1. Accept a `topic` string and optional `focus` string.

2. Run 2–4 web searches covering:
   - A broad overview of the topic
   - Key concepts and terminology
   - If `focus` is provided, searches targeted at that angle

3. For each search, collect the top relevant results. Visit pages as needed to extract accurate detail.

4. Compile findings into a structured report:
   - **Summary** — 2–4 sentences describing the topic at a high level
   - **Key concepts** — bulleted list of important terms and ideas with brief definitions
   - **Sources** — list of URLs consulted, each with a one-line description of what was found there
   - **Suggested course angles** — 2–3 ways this topic could be framed for a learning audience

5. Return the report to the caller. Do not write any files.
