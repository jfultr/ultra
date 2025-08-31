### Render the business plan with Python

#### Option A: Conda (preferred)

- **Create a Conda environment and install dependencies**
```bash
cd /home/jfultr/shared_context_saas
conda create -n plan-docs python=3.12 -y
conda activate plan-docs
pip install "Jinja2>=3.1" "PyYAML>=6.0"
```

- **Render the plan** (writes `docs/plan/plan.md`)
```bash
python - <<'PY'
import pathlib
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

base = pathlib.Path("/home/jfultr/shared_context_saas")
template_dir = base / "docs" / "plan"
yaml_path = template_dir / "example_plan.yaml"
template_name = "plan.md.j2"
output_path = template_dir / "plan.md"

env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(["md", "md.j2"]) 
)

with open(yaml_path, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

template = env.get_template(template_name)
rendered = template.render(**data)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(rendered)

print(f"Wrote {output_path}")
PY
```

- **Open the result**
```bash
cat /home/jfultr/shared_context_saas/docs/plan/plan.md
```

### Render to Markdown / HTML / PDF via CLI

- **Install extra deps for HTML/PDF**
```bash
conda activate plan-docs  # or your venv
pip install markdown weasyprint
```

- **Install WeasyPrint system deps (choose ONE path):**
  - Ubuntu/WSL (apt):
    ```bash
    sudo apt update
    sudo apt install -y libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 libffi8 libpangoft2-1.0-0
    ```
  - Conda (conda-forge):
    ```bash
    conda install -c conda-forge weasyprint pango cairo gdk-pixbuf libffi -y
    ```
  If still missing fonts, add: `sudo apt install -y fonts-dejavu-core` (or install a font package via Conda).

- **Use the renderer script** (located at `docs/plan/render.py`)
```bash
# Markdown
python /home/jfultr/shared_context_saas/docs/plan/render.py --engine md

# HTML
python /home/jfultr/shared_context_saas/docs/plan/render.py --engine html --out /home/jfultr/shared_context_saas/docs/plan/plan.html

# PDF (via WeasyPrint)
python /home/jfultr/shared_context_saas/docs/plan/render.py --engine pdf --out /home/jfultr/shared_context_saas/docs/plan/plan.pdf
```

- **Options**
```bash
python docs/plan/render.py --help
# --engine {md,html,pdf}  Output engine (default: md)
# --data PATH             YAML file (default: example_plan.yaml)
# --template PATH         Template file (default: plan.md.j2)
# --out PATH              Output path (default: plan.{md|html|pdf})
# --title TITLE           Override HTML/PDF title
```

#### Option B: Python venv

- **Create a virtual environment and install dependencies**
```bash
cd /home/jfultr/shared_context_saas
python3 -m venv .venv
source .venv/bin/activate
pip install "Jinja2>=3.1" "PyYAML>=6.0"
```

- **Render the plan** (writes `docs/plan/plan.md`)
```bash
python - <<'PY'
import pathlib
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

base = pathlib.Path("/home/jfultr/shared_context_saas")
template_dir = base / "docs" / "plan"
yaml_path = template_dir / "example_plan.yaml"
template_name = "plan.md.j2"
output_path = template_dir / "plan.md"

env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(["md", "md.j2"]) 
)

with open(yaml_path, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

template = env.get_template(template_name)
rendered = template.render(**data)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(rendered)

print(f"Wrote {output_path}")
PY
```

- **Open the result**
```bash
cat /home/jfultr/shared_context_saas/docs/plan/plan.md
```


