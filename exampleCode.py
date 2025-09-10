#!/usr/bin/env python3
"""
md_to_json.py

Convert a privacy-policy draft Markdown file into a structured JSON file.
- Output is written next to the draft as YYYY-MM-DD.json (from "Last Updated:").
- Converts common inline Markdown to HTML so your website can render it directly.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
import argparse

# ---------- Helpers ----------

def slugify(text: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9]+', '-', text.strip().lower())
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s or "app"

def _try_parse_date(raw: str) -> datetime:
    """
    UK-oriented parser:
      - dd/mm/yyyy
      - dd-mm-yyyy
      - dd.mm.yyyy
      - dd Mon yyyy   (e.g., 01 Jan 2025)
      - dd Month yyyy (e.g., 01 January 2025)
    """
    raw = raw.strip()
    fmts = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%d %b %Y",
        "%d %B %Y",
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    # Last resort: extract digits as DD MM YYYY (UK order)
    digits = re.findall(r"\d+", raw)
    if len(digits) >= 3:
        d, mth, y = map(int, digits[:3])
        return datetime(y, mth, d)
    raise ValueError(f"Unrecognised UK date format: {raw!r}")

def parse_last_updated(md_text: str) -> datetime:
    """
    Finds a 'Last Updated' style line and parses the UK-style date.
    Accepts variants like:
      Last Updated: 01/01/2025
      Last updated - 1-1-2025
      Updated 01.01.2025
      Effective Date: 01 Jan 2025
      Effective as of — 01 January 2025
    """
    normalised = md_text.replace("—", "-").replace("–", "-").replace("：", ":")
    patterns = [
        r'(?im)^\s*last\s*updated\s*[:\-]?\s*(.+?)\s*$',
        r'(?im)^\s*updated\s*[:\-]?\s*(.+?)\s*$',
        r'(?im)^\s*effective\s*(?:date|as\s*of)\s*[:\-]?\s*(.+?)\s*$',
    ]
    for pat in patterns:
        m = re.search(pat, normalised)
        if m:
            return _try_parse_date(m.group(1))
    # Fallback: first UK-style date anywhere (dd[./-]mm[./-]yyyy)
    m = re.search(r'(\d{1,2}[./-]\d{1,2}[./-]\d{4})', normalised)
    if m:
        return _try_parse_date(m.group(1))
    raise ValueError("Could not find a UK-style 'Last Updated' / 'Updated' / 'Effective Date' line.")

def extract_title_and_app(md_text: str):
    """
    Extract H1 '# ...' and app name from parentheses if present.
    Example: '# Privacy Policy (Trail Pacing)' -> ('Privacy Policy (Trail Pacing)', 'Trail Pacing')
    """
    m = re.search(r'(?m)^\s*#\s+(.+?)\s*$', md_text)
    if not m:
        raise ValueError("Could not find a top-level '# ' title in the markdown.")
    title = m.group(1).strip()
    m_app = re.search(r'\(([^)]+)\)', title)
    app_name = m_app.group(1).strip() if m_app else None
    return title, app_name

def derive_app_id(app_name: str | None, md_path: Path) -> str:
    """
    Prefer app name from H1 parentheses; else infer from path like apps/<appId>/...; else use parent dir.
    """
    if app_name:
        return slugify(app_name)
    parts = md_path.resolve().parts
    if "apps" in parts:
        idx = parts.index("apps")
        if idx + 1 < len(parts):
            return slugify(parts[idx + 1])
    return slugify(md_path.parent.name or md_path.stem)

# -------- Markdown → HTML Conversion --------
_md_code = re.compile(r'`([^`]+)`')
_md_strong = re.compile(r'\*\*([^*][\s\S]*?)\*\*|__([^_][\s\S]*?)__')
_md_em = re.compile(r'(?<!\*)\*([^*][\s\S]*?)\*(?!\*)|_([^_][\s\S]*?)_')
_md_link = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
_md_two_space_break = re.compile(r'  \n')  # two spaces + newline -> <br>

def convert_markdown_to_html(text: str) -> str:
    """
    Convert Markdown to HTML, handling:
    - Headers (### -> <h3>)
    - Lists (- item -> <li>item</li>)
    - Blockquotes (> text -> <blockquote>)
    - Inline formatting (**bold**, *italic*, `code`, [links])
    - Paragraphs and line breaks
    """
    if not text:
        return text

    # Convert headers first (### -> <h3>)
    text = re.sub(r'^###\s+(.+?)$', r'<h3 class="text-lg font-medium text-gray-900 mt-4 mb-2">\1</h3>', text, flags=re.MULTILINE)
    
    # Convert lists and blockquotes (- item -> <li>item</li>, > text -> <blockquote>)
    # Handle both single items and multi-line lists
    lines = text.split('\n')
    in_list = False
    in_blockquote = False
    list_items = []
    blockquote_items = []
    result_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('- '):
            # Start or continue a list
            if not in_list:
                in_list = True
                list_items = []
            list_items.append(line[2:])  # Remove the "- " prefix
        elif line.startswith('-'):
            # Handle cases where there's no space after dash
            if not in_list:
                in_list = True
                list_items = []
            list_items.append(line[1:].strip())
        elif line.startswith('> '):
            # Start or continue a blockquote
            if not in_blockquote:
                in_blockquote = True
                blockquote_items = []
            blockquote_items.append(line[2:])  # Remove the "> " prefix
        elif line.startswith('>'):
            # Handle cases where there's no space after >
            if not in_blockquote:
                in_blockquote = True
                blockquote_items = []
            blockquote_items.append(line[1:].strip())
        elif in_list and line:
            # Continue the previous list item (multi-line content)
            if list_items:
                list_items[-1] += ' ' + line
        elif in_blockquote and line:
            # Continue the previous blockquote item (multi-line content)
            if blockquote_items:
                blockquote_items[-1] += ' ' + line
        elif (in_list or in_blockquote) and not line:
            # Empty line - end the list or blockquote
            if in_list and list_items:
                result_lines.append('<ul class="list-disc list-outside mb-4 space-y-1 pl-5">')
                for item in list_items:
                    result_lines.append(f'<li>{convert_inline_markdown(item)}</li>')
                result_lines.append('</ul>')
                list_items = []
                in_list = False
            if in_blockquote and blockquote_items:
                result_lines.append('<div class="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-600 rounded-r-lg px-4 py-2 mb-4 shadow-sm">')
                result_lines.append('<div class="flex items-start">')
                result_lines.append('<div class="flex-shrink-0 mr-3">')
                result_lines.append('<svg class="w-5 h-5 text-blue-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">')
                result_lines.append('<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>')
                result_lines.append('</svg>')
                result_lines.append('</div>')
                result_lines.append('<div class="flex-1">')
                for item in blockquote_items:
                    result_lines.append(f'<p class="text-gray-800 font-medium leading-tight mb-0">{convert_inline_markdown(item)}</p>')
                result_lines.append('</div>')
                result_lines.append('</div>')
                result_lines.append('</div>')
                blockquote_items = []
                in_blockquote = False
        else:
            # Regular content
            if in_list and list_items:
                # End the list before this content
                result_lines.append('<ul class="list-disc list-inside mb-4 space-y-1">')
                for item in list_items:
                    result_lines.append(f'<li>{convert_inline_markdown(item)}</li>')
                result_lines.append('</ul>')
                list_items = []
                in_list = False
            
            if in_blockquote and blockquote_items:
                # End the blockquote before this content
                result_lines.append('<div class="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-600 rounded-r-lg px-4 py-2 mb-4 shadow-sm">')
                result_lines.append('<div class="flex items-start">')
                result_lines.append('<div class="flex-shrink-0 mr-3">')
                result_lines.append('<svg class="w-5 h-5 text-blue-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">')
                result_lines.append('<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>')
                result_lines.append('</svg>')
                result_lines.append('</div>')
                result_lines.append('<div class="flex-1">')
                for item in blockquote_items:
                    result_lines.append(f'<p class="text-gray-800 font-medium leading-tight mb-0">{convert_inline_markdown(item)}</p>')
                result_lines.append('</div>')
                result_lines.append('</div>')
                result_lines.append('</div>')
                blockquote_items = []
                in_blockquote = False
            
            if line:
                result_lines.append(f'<p class="mb-4">{convert_inline_markdown(line)}</p>')
    
    # Handle any remaining list or blockquote at the end
    if in_list and list_items:
        result_lines.append('<ul class="list-disc list-outside mb-4 space-y-1 pl-5">')
        for item in list_items:
            result_lines.append(f'<li>{convert_inline_markdown(item)}</li>')
        result_lines.append('</ul>')
    
    if in_blockquote and blockquote_items:
        result_lines.append('<div class="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-600 rounded-r-lg px-4 py-2 mb-4 shadow-sm">')
        result_lines.append('<div class="flex items-start">')
        result_lines.append('<div class="flex-shrink-0 mr-3">')
        result_lines.append('<svg class="w-5 h-5 text-blue-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">')
        result_lines.append('<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>')
        result_lines.append('</svg>')
        result_lines.append('</div>')
        result_lines.append('<div class="flex-1">')
        for item in blockquote_items:
            result_lines.append(f'<p class="text-gray-800 font-medium leading-relaxed">{convert_inline_markdown(item)}</p>')
        result_lines.append('</div>')
        result_lines.append('</div>')
        result_lines.append('</div>')
    
    return '\n'.join(result_lines)

def convert_inline_markdown(text: str) -> str:
    """
    Convert inline Markdown to HTML:
      - **bold** / __bold__  -> <strong>
      - *italic* / _italic_  -> <em>
      - `code`               -> <code>
      - [text](url)          -> <a href>
      - two-space line breaks -> <br>
    """
    if not text:
        return text

    # Convert code first to avoid nested replacements
    text = _md_code.sub(lambda m: f"<code class='bg-gray-100 px-1 py-0.5 rounded text-sm'>{m.group(1)}</code>", text)

    # Strong
    def _strong_sub(m):
        inner = m.group(1) if m.group(1) is not None else m.group(2)
        return f"<strong>{inner}</strong>"
    text = _md_strong.sub(_strong_sub, text)

    # Emphasis
    def _em_sub(m):
        inner = m.group(1) if m.group(1) is not None else m.group(2)
        return f"<em>{inner}</em>"
    text = _md_em.sub(_em_sub, text)

    # Links
    text = _md_link.sub(r'<a href="\2" class="text-primary hover:text-blue-600 underline">\1</a>', text)

    # Hard line breaks (Markdown's two-space break)
    text = _md_two_space_break.sub("<br>\n", text)

    return text

def parse_sections(md_text: str):
    """
    Parses level-2 sections '## Heading'. Returns list of {heading, content:[paragraphs]}.
    Converts all Markdown content to proper HTML.
    """
    matches = list(re.finditer(r'(?m)^\s*##\s+(.+?)\s*$', md_text))
    sections = []
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        body = md_text[start:end].strip()

        # Convert the entire section body to HTML
        html_content = convert_markdown_to_html(body)
        
        # Split into content blocks (paragraphs, lists, headers)
        content_blocks = [block.strip() for block in html_content.split('\n') if block.strip()]
        
        sections.append({"heading": heading, "content": content_blocks})
    return sections

def md_to_json_structure(md_path: Path, version: str, locale: str):
    md_text = md_path.read_text(encoding="utf-8")
    title, app_name = extract_title_and_app(md_text)
    last_dt = parse_last_updated(md_text)
    sections = parse_sections(md_text)
    app_id = derive_app_id(app_name, md_path)
    effective_iso = last_dt.strftime("%Y-%m-%d")

    return {
        "appId": app_id,
        "title": title,
        "sections": sections,
        "metadata": {
            "version": version,
            "lastUpdated": effective_iso,
            "effectiveDate": effective_iso,
            "locale": locale,
        }
    }, last_dt

# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(description="Convert privacy-policy draft.md to JSON.")
    parser.add_argument("drafts", nargs="+", help="Path(s) to draft.md file(s).")
    parser.add_argument("--version", default="1.0.0", help="Metadata version (default: 1.0.0).")
    parser.add_argument("--locale", default="en-GB", help="Metadata locale (default: en-GB).")
    parser.add_argument("--stdout", action="store_true", help="Print JSON to stdout instead of writing files.")
    args = parser.parse_args()

    for draft in args.drafts:
        md_path = Path(draft)
        if not md_path.exists():
            print(f"[skip] File not found: {md_path}")
            continue

        try:
            data, last_dt = md_to_json_structure(md_path, version=args.version, locale=args.locale)
        except Exception as e:
            print(f"[error] {md_path}: {e}")
            continue

        out_name = f"{last_dt.strftime('%Y-%m-%d')}.json"
        out_path = md_path.parent / out_name

        if args.stdout:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"[ok] Wrote {out_path}")

if __name__ == "__main__":
    main()

# python3 md_to_json.py draft.md
