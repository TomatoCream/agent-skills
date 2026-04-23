# Setting Up a Python Data Analysis Project

Here is a recommended modern, zero-friction setup for a Python data analysis project using **uv** (fast Python package manager) and **direnv** (automatic virtual environment activation).

---

## Step 1: Machine-Level Setup (one-time)

Install `uv` and `direnv`, then configure them so every future project gets automatic environment activation:

```bash
brew install uv direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc
```

Create a custom direnv function that automatically creates and activates a uv-managed virtual environment:

```bash
mkdir -p ~/.config/direnv
cat > ~/.config/direnv/direnvrc << 'EOF'
use_uv() {
    if [ ! -d .venv ]; then
        uv venv
    fi
    source .venv/bin/activate
    uv sync
}
EOF
```

Globally ignore `.envrc` files from git so they never get committed:

```bash
mkdir -p ~/.config/git
echo ".envrc" >> ~/.config/git/ignore
```

**Why this matters:** After this one-time setup, every new project you create will automatically activate its virtual environment when you `cd` into the directory. No more `source .venv/bin/activate` ever again.

---

## Step 2: Per-Project Setup

Create the project and install your data analysis stack:

```bash
mkdir my-analysis && cd my-analysis
uv init --app
uv add plotly pandas numpy scipy kaleido nbformat
echo "use_uv" > .envrc
direnv allow
```

That is the entire setup. When you `cd` into `my-analysis`, direnv automatically runs `use_uv`, which creates the virtual environment (if needed), activates it, and syncs dependencies. When you `cd` out, it deactivates.

---

## Step 3: Choose Your Dependency Tier

Not every project needs every package. Start with the minimum and add what you need:

| Tier | Packages | When to Use |
|------|----------|-------------|
| **Minimum** | `plotly pandas numpy` | Any visualization or data analysis work |
| **Statistical** | + `scipy` | Distribution fitting, hypothesis testing, statistical charts |
| **ML Viz** | + `scikit-learn` | PCA, confusion matrices, ROC curves, feature importance |
| **Export** | + `kaleido` | Static PNG/PDF/SVG export of Plotly charts |
| **Notebooks** | + `nbformat jupyterlab` | Interactive notebook workflows |
| **Dashboards** | + `dash` | Production interactive dashboards |
| **Alt engines** | `matplotlib seaborn altair` | Publication-quality static figures, grammar-of-graphics |

For a general data analysis project, the recommended starting point is the **Statistical + Export + Notebooks** tier:

```bash
uv add plotly pandas numpy scipy kaleido nbformat jupyterlab
```

This gives you interactive charts (Plotly), data manipulation (pandas/numpy), statistical testing (scipy), static image export (kaleido), and a notebook environment (JupyterLab).

---

## Step 4: Verify the Setup

Run this quick sanity check to confirm everything works:

```bash
uv run python -c "
import pandas as pd
import numpy as np
import plotly.express as px

df = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100),
    'group': np.random.choice(['A', 'B'], 100)
})
fig = px.scatter(df, x='x', y='y', color='group', template='plotly_white')
fig.write_html('test_chart.html')
print('Setup verified -- test_chart.html created.')
"
```

Open `test_chart.html` in a browser to see an interactive scatter plot.

---

## Step 5: Suggested Project Structure

```
my-analysis/
  .venv/              # auto-created by direnv/uv
  .envrc              # contains "use_uv" -- globally gitignored
  pyproject.toml      # uv manages this -- your single source of truth for deps
  uv.lock             # deterministic lock file -- commit this
  data/
    raw/              # immutable original data
    processed/        # cleaned/transformed data
  notebooks/          # Jupyter notebooks for exploration
  src/
    __init__.py
    analysis.py       # reusable analysis functions
    charts.py         # reusable visualization functions
  outputs/
    figures/          # exported charts (PNG, PDF, HTML)
    reports/          # final deliverables
```

---

## Why This Stack?

- **uv over pip/conda**: uv resolves and installs dependencies 10-100x faster than pip. It replaces pip, pip-tools, virtualenv, and pyenv in a single binary. `pyproject.toml` + `uv.lock` give you reproducible environments without conda's overhead.
- **direnv over manual activation**: Eliminates the single most common friction point in Python development -- forgetting to activate the virtual environment. It is automatic and invisible.
- **Plotly as the default visualization library**: Interactive by default (hover, zoom, pan), works in notebooks and standalone HTML, has a high-level Express API that covers 90% of use cases, and you can drop down to Graph Objects for full control. For publication-quality static figures destined for journals, add `matplotlib` + `seaborn` as an alternative engine.
- **pandas + numpy as the data layer**: The standard for tabular data manipulation in Python. pandas provides the DataFrame abstraction; numpy provides the numerical foundation underneath.
- **scipy for statistics**: Distribution fitting, hypothesis testing, and statistical computations that go beyond what pandas offers natively.

---

## Quick Reference: Common Commands

| Task | Command |
|------|---------|
| Add a package | `uv add <package>` |
| Remove a package | `uv remove <package>` |
| Run a script | `uv run python script.py` |
| Launch JupyterLab | `uv run jupyter lab` |
| Update all deps | `uv lock --upgrade && uv sync` |
| Export requirements.txt | `uv pip compile pyproject.toml -o requirements.txt` |

This setup gets you from zero to a working data analysis environment in under two minutes, with automatic environment management from that point forward.
