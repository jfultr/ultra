#!/usr/bin/env python3
"""
Render the business plan from YAML + Jinja2 into Markdown, HTML, or PDF.

Usage examples:
  - Markdown: python docs/plan/render.py --engine md
  - HTML:     python docs/plan/render.py --engine html
  - PDF:      python docs/plan/render.py --engine pdf
"""

from __future__ import annotations

import argparse
import sys
import pathlib
from typing import Any, Dict

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


DEFAULT_TEMPLATE = "plan.md.j2"
DEFAULT_DATA = "example_plan.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render business plan")
    parser.add_argument(
        "--engine",
        choices=["md", "html", "pdf"],
        default="md",
        help="Output format/engine"
    )
    parser.add_argument(
        "--data",
        default=str(pathlib.Path(__file__).with_name(DEFAULT_DATA)),
        help="Path to YAML data file"
    )
    parser.add_argument(
        "--template",
        default=str(pathlib.Path(__file__).with_name(DEFAULT_TEMPLATE)),
        help="Path to Jinja2 Markdown template (.md.j2)"
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output file path. Defaults to docs/plan/plan.{md|html|pdf}"
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Override document title for HTML/PDF wrapper"
    )
    return parser.parse_args()


def load_yaml_data(yaml_path: pathlib.Path) -> Dict[str, Any]:
    with yaml_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def render_markdown_from_template(template_path: pathlib.Path, data: Dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["md", "md.j2"])  # no autoescape for md by default
    )
    template = env.get_template(template_path.name)
    return template.render(**data)


def convert_markdown_to_html(markdown_text: str, page_title: str) -> str:
    try:
        import markdown as md
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: markdown. Install with `pip install markdown` or `conda install -c conda-forge markdown`."
        ) from exc

    body = md.markdown(
        markdown_text,
        extensions=[
            "extra",
            "tables",
            "toc",
            "sane_lists",
            "smarty",
        ],
        output_format="html5",
    )

    html = f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{page_title}</title>
    <style>
      :root {{
        --text: #1f2937;
        --muted: #4b5563;
        --border: #e5e7eb;
      }}
      @page {{
        size: A4;
        margin: 24mm 18mm;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji";
        color: var(--text);
        line-height: 1.6;
      }}
      h1, h2, h3, h4 {{
        line-height: 1.25;
        margin: 1.6em 0 0.6em;
      }}
      h1 {{ font-size: 1.875rem; }}
      h2 {{ font-size: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.25rem; }}
      h3 {{ font-size: 1.25rem; }}
      p {{ margin: 0.6em 0; }}
      ul, ol {{ padding-left: 1.25rem; }}
      code {{ background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 4px; }}
      pre code {{ display: block; padding: 0.75rem; }}
      table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
      th, td {{ border: 1px solid var(--border); padding: 0.5rem 0.6rem; text-align: left; }}
      thead th {{ background: #f9fafb; }}
    </style>
  </head>
  <body>
    {body}
  </body>
</html>
"""
    return html


def write_text(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content)


def write_pdf_from_html(html_text: str, output_path: pathlib.Path, base_url: str | None = None) -> None:
    try:
        from weasyprint import HTML
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: weasyprint. Install with `pip install weasyprint` or `conda install -c conda-forge weasyprint`."
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_text, base_url=base_url).write_pdf(str(output_path))


def main() -> int:
    args = parse_args()

    template_path = pathlib.Path(args.template).resolve()
    yaml_path = pathlib.Path(args.data).resolve()
    base_dir = template_path.parent

    # Determine output path
    if args.out is not None:
        out_path = pathlib.Path(args.out).resolve()
    else:
        default_name = {
            "md": "plan.md",
            "html": "plan.html",
            "pdf": "plan.pdf",
        }[args.engine]
        out_path = base_dir / default_name

    # Load and render
    data = load_yaml_data(yaml_path)
    markdown_text = render_markdown_from_template(template_path, data)

    if args.engine == "md":
        write_text(out_path, markdown_text)
        print(f"Wrote {out_path}")
        return 0

    # Determine title
    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    page_title = args.title or meta.get("title") or "Business Plan"

    html_text = convert_markdown_to_html(markdown_text, page_title)

    if args.engine == "html":
        write_text(out_path, html_text)
        print(f"Wrote {out_path}")
        return 0

    if args.engine == "pdf":
        base_url = str(base_dir)
        write_pdf_from_html(html_text, out_path, base_url=base_url)
        print(f"Wrote {out_path}")
        return 0

    raise SystemExit(f"Unknown engine: {args.engine}")


if __name__ == "__main__":
    sys.exit(main())


