# Langfuse Cost Analysis

Jupyter notebooks for analyzing LLM usage and costs from [Langfuse](https://langfuse.com) (self-hosted at `langfuse.kavida.ai`).

## Setup

1. **Clone** (if needed):
   ```bash
   git clone https://github.com/SartJnKv/Langfuse.git
   cd Langfuse
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install langfuse tqdm
   ```

4. **Configure credentials** (do not commit keys). Set environment variables:
   - `LANGFUSE_PUBLIC_KEY` — your Langfuse public key (`pk-lf-...`)
   - `LANGFUSE_SECRET_KEY` — your Langfuse secret key (`sk-lf-...`)
   - `LANGFUSE_HOST` — e.g. `https://langfuse.kavida.ai` or `https://cloud.langfuse.com`

   Or create a `.env` file (ignored by git) and load it before running the notebook.

## Notebooks

- **cost.ipynb** — Fetch traces for a date range (IST), compute costs, and summarize usage.
- **06_langfuse_cost_analysis.ipynb** — Alternate cost analysis workflow.

## Usage

Open a notebook in Jupyter or VS Code, set the date range in the config cell, then run all cells. Ensure `LANGFUSE_*` env vars are set so the notebook can connect to Langfuse.

## License

Use as needed for your organization.
