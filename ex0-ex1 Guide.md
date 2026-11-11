# ex0 & ex1 — The User Guide 🧪🔮

Welcome to the first two rooms of the laboratory. This guide explains everything these two exercises do, why they do it, and how to run them from scratch — written so you can bounce back to it whenever a concept gets foggy.

**What's in here:**

- ex0 — The Sealed Laboratory: detect your Python environment, check your dependencies, run a small data pipeline
- ex1 — The Oracle: configure a program with environment variables and a `.env` file, secrets safely out of the code

---

# Before Anything: The Virtual Environment 🧪

## What it IS

A virtual environment (venv) is an **isolated copy of a Python setup**: its own python binary, its own `site-packages` folder, its own installed packages. Install something inside it, and it doesn't touch the rest of your system.

```
GLOBAL (system-wide)                    VIRTUAL (your lab)
─────────────────────────               ─────────────────────────
/usr/bin/python3                        matrix_env/bin/python3
/usr/lib/python3.x/site-packages   ←    matrix_env/lib/python3.x/site-packages
everything you install                  only what THIS project needs
leaks into every project 💀             sealed from the outside ✨
```

## What it's FOR (uses)

- **Dependency isolation** — project A needs `pandas 2.1`, project B needs `pandas 1.0`. Without venvs they fight; with venvs each has its own copy.
- **Reproducibility** — hand someone your `requirements.txt`, they rebuild your exact environment.
- **Clean system** — no `sudo pip install` polluting the OS Python. Ever.
- **Safety** — a broken package in the venv ruins only the venv. Delete the folder, start over.

## The venv cheatsheet — full sequence

Run from the project root:

```bash
# 1. create the lab
python3 -m venv matrix_env

# 2. seal yourself in
source matrix_env/bin/activate        # Linux/macOS
matrix_env\Scripts\activate           # Windows

#    → your prompt now shows (matrix_env). That's the seal ✨

# 3. stock the reagents (ex0 + ex1 together)
python3 -m pip install -r ex0/requirements.txt
python3 -m pip install -r ex1/requirements.txt

#    (python3 -m pip, never bare pip — guarantees packages land
#     in THIS python and not some random other one)

# 4. run things
python3 ex0/construct.py
python3 ex0/loading.py
cp ex1/.env.example ex1/.env          # then edit ex1/.env
python3 ex1/oracle.py

# 5. leave when done
deactivate
```

One venv covers both exercises — they're the same project. And never commit `matrix_env/` to git: anyone can recreate it in seconds with the commands above, which is exactly the point.

---

# ex0 — The Sealed Laboratory 🧪

This exercise has two halves: **Part 1** (`construct.py`) checks whether you're working in a sealed environment, and **Part 2** (`loading.py`) checks that your external libraries (the "reagents") are installed, then runs a small demo pipeline with them.

Files in `ex0/`:

| file | job |
|---|---|
| `construct.py` | venv detection + environment report |
| `loading.py` | dependency check + the demo pipeline |
| `requirements.txt` | dependency declaration for pip |
| `pyproject.toml` | dependency declaration for Poetry |

## Part 1 — `construct.py`: the one-line venv detector

The program's whole brain:

```python
def is_virtual() -> bool:
    return sys.prefix != sys.base_prefix
```

Three `sys` attributes do the magic:

```
sys.executable   → path to the python binary RUNNING you     (/home/you/matrix_env/bin/python)
sys.prefix       → path to the CURRENT environment's home    (/home/you/matrix_env)
sys.base_prefix  → path to the BASE python the venv is from  (/usr/bin)
```

```
sys.prefix == sys.base_prefix  →  GLOBAL environment  (no venv)
sys.prefix != sys.base_prefix  →  VIRTUAL environment (sealed!) ✅
```

Outside a venv, both point to the same place. Inside one, `prefix` moves to the venv while `base_prefix` still points at the original system Python. Comparing them = instant detection.

### The three libraries at work

| library | boss of | used here for |
|---|---|---|
| `sys` | the interpreter | `executable`, `prefix`, `base_prefix` |
| `os` | the operating system | `os.path.basename(sys.prefix)` → the venv's NAME ("matrix_env") |
| `site` | package paths | `site.getsitepackages()` → where installed packages live |

`os.path.basename()` strips a path down to its last piece:

```python
sys.prefix                      # '/home/you/matrix_env'
os.path.basename(sys.prefix)    # 'matrix_env'  ← just the name
```

(Its sibling `os.path.dirname()` does the opposite: keeps everything EXCEPT the last piece.)

### The program's two faces

```
OUTSIDE a venv                      INSIDE a venv
─────────────────────────           ─────────────────────────
"WARNING: You are in the           "SUCCESS: You are in an
 global environment!"                isolated environment!"
+ instructions to seal:             + shows where packages install
  python3 -m venv matrix_env          (the venv's site-packages)
  source matrix_env/bin/activate    (Unix)
  matrix_env\Scripts\activate       (Windows)
```

That Windows line needs a **raw string**: `r"matrix_env\Scripts\activate"`. The `r` prefix tells Python "don't treat backslashes as escape characters" — normally `\S` would either break or get silently mangled. Raw string = the backslashes print exactly as typed.

### `if __name__ == "__main__":`

The doorbell of every Python script. Python gives the running file the special name `__main__`, so this guard means "only run `main()` if this file was executed directly" — not when it's imported by another file. (And mind the double underscores — `"main"` with single underscores never matches, and `main()` silently never runs. Classic.)

## Part 2 — `loading.py`: dependency check + demo pipeline

### Checking a library WITHOUT importing it

```python
importlib.metadata.version("pandas")   # → "2.1.0"
```

This is the detective trick: it reads the package's **`dist-info/METADATA` files on disk** — it never imports the package. Two big consequences:

1. Works even if the package is broken or unimportable
2. Raises `importlib.metadata.PackageNotFoundError` when missing → caught → prints `[KO]` + install instructions instead of crashing

### The structure

```
show_instructions()   → prints pip AND Poetry install commands
check_pandas()        → version("pandas") == "2.1.0" ? [OK] : [KO]
check_numpy()         → same pattern
check_matplotlib()    → same pattern
check_dependencies()  → calls the three above
main()                → guard the check, then run the demo
```

The fail-fast guard in `main()`:

```python
try:
    check_dependencies()
except Exception:
    sys.exit(1)
```

Anything explodes during the check → terminate immediately with exit code 1. Better to die here with a clear reason than crash at line 70 with a cryptic `NameError`. (Exit codes are a whole language: **0 = success, non-zero = something went wrong**. Shells and scripts read them.)

### pip vs Poetry — two ways to declare your reagents

```
requirements.txt (pip)              pyproject.toml + poetry.lock (Poetry)
─────────────────────────────       ───────────────────────────────────────
pandas==2.1.0                       same constraints declared
pip resolves fresh each install     + poetry.lock FREEZES the resolution
"whatever works today"              "identical install, every time" 🔒
```

- `==` is a **pin**: exactly this version, no negotiation
- pip figures out versions fresh at every install — two installs can differ
- Poetry freezes its resolution into a lockfile, so every install is byte-identical

Anatomy of the `pyproject.toml`:

```toml
[tool.poetry.dependencies]     # Poetry-specific settings
python = ">=3.10"              #   Python version requirement (>= = or newer)

[project]                      # the project's identity card
name = "loading"
version = "0.1.0"
dependencies = [               # the reagent shelf
  "pandas==2.1.0",             #   == = exact version pin
  "numpy==1.25.0",
  "matplotlib==3.7.2"
]
```

### The demo pipeline: numpy → pandas → matplotlib 🏃‍♀️

A relay race — each runner does one job and hands the baton:

```
np.random.choice(2000, 1000, replace=False)     numpy: the number factory
np.sort(...)                                    1000 unique sorted ints
        │
        ▼
pd.DataFrame({"matrix_data": matrix_data})      pandas: labeled packaging
        │                                       dict: key = column name,
        ▼                                        value = the array
df.plot()                                       draws a chart of every
        │                                       numeric column vs the index
        ▼
plt.savefig("matrix_analysis.png")              matplotlib: writes the
                                                current figure to a file
```

Why not `plt.plot(matrix_data)` directly? Each library doing what it's best at:

- **numpy** — contiguous C arrays, vectorized ops. `choice(2000, 1000, replace=False)` = "deal 1000 unique cards from a 2000-card deck"; `sort` puts them in order. Python lists can't touch this speed.
- **pandas** — the dict `{"matrix_data": array}` becomes a table where the key is the column name — which means the chart gets a proper label for free
- **matplotlib** — the rendering engine. `savefig` is the **headless export**: it writes the figure to a file instead of popping a GUI window (perfect for scripts and servers)

### The names decoded

| name | kind | belongs to |
|---|---|---|
| `pd` / `plt` | aliases chosen at import (`import x as y`) | pandas / matplotlib.pyplot |
| `npt` | alias for `numpy.typing` — annotation tools, zero runtime effect | numpy's typing submodule |
| `df` | just a variable name for the table | — |
| `npt.NDArray` | type hint so checkers/editors understand your code | numpy.typing |
| `df.plot()` | method on the DataFrame | pandas (matplotlib underneath) |
| `plt.savefig()` | writes the "current figure" to disk | matplotlib |

One last import trick in `loading.py`:

```python
try:
    import numpy as np
    ...
except ModuleNotFoundError:
    pass
```

If the libraries aren't installed, imports are silently skipped — so the file can still start and report WHICH reagents are missing (via `importlib.metadata`) instead of dying at the import line.

---

# ex1 — The Oracle 🔮

Programs need secrets: API keys, database URLs, endpoints. Write them as constants in your source code and they're one `git push` away from the whole world. The Oracle does it the right way: **configuration lives in the environment, secrets live next to the code but never inside it.**

Files in `ex1/`:

| file | job |
|---|---|
| `oracle.py` | loads and displays configuration, dev/prod modes |
| `requirements.txt` | the one external library: `python-dotenv` |
| `.env.example` | committed template with placeholder values |
| `.gitignore` | keeps `.env` OUT of git |

## The core idea: the priority ladder 🪜

```
┌──────────────────────────────────────────────┐
│  1. Real environment variables   ← WINS      │
│  2. .env file (via load_dotenv)              │
│  3. Defaults in code (fallback)              │
└──────────────────────────────────────────────┘
```

The magic ingredient: **`load_dotenv()` never overrides variables that already exist.** So when you run:

```bash
MATRIX_MODE=production API_KEY=secret123 python3 ex1/oracle.py
```

the shell variables are already in `os.environ` before the script starts, `load_dotenv()` sees them occupied and skips the `.env` values → **shell beats `.env` for free, with zero extra code.**

## The `.env` family

| file | contents | committed? |
|---|---|---|
| `.env` | REAL values (your secrets) | ❌ gitignored |
| `.env.example` | placeholder template | ✅ committed |

The workflow: `cp .env.example .env` → edit `.env` → run. The template is a frozen menu; `.env` is your order.

A valid `.env.example`:

```env
# development or production
MATRIX_MODE=development
DATABASE_URL=sqlite:///oracle.db
API_KEY=your-api-key-here
LOG_LEVEL=DEBUG
ZION_ENDPOINT=https://zion.example.com
```

Why these choices:

- **`sqlite:///oracle.db`** — SQLite is a serverless database: the whole database is ONE file. No server, no setup, and Python ships with it built in. Perfect for development. The triple slash is the standard SQLite URL format meaning "a local file."
- **`zion.example.com`** — `.example.com` is officially reserved for documentation, so it's guaranteed fake. It shows the SHAPE of the value without pretending to be real.
- **`your-api-key-here`** — obviously fake placeholder. The file gets committed, so every value in it must be plausible but fake.

Rules of `.env` files: `KEY=value`, one per line, no quotes needed, comments start with `#`, no spaces around `=`.

And the `.gitignore`:

```
.env
__pycache__/
*.pyc
```

**Why `.env` must be ignored:** git history keeps everything forever. Push a real secret once, and deleting it later doesn't help — it's still in the history. `.env.example` documents which keys exist without leaking anything.

## The tools

### `os.getenv()` — read an environment variable, politely

```python
os.getenv("MATRIX_MODE")                 # None if missing (no crash)
os.getenv("MATRIX_MODE", "development")  # default kicks in if missing
```

vs `os.environ["MATRIX_MODE"]`, which raises `KeyError` and kills the program 💀. For a "never crash" tool, always `getenv` with a default.

### `python-dotenv` — the bridge between file and environment

```python
from dotenv import load_dotenv
load_dotenv()   # finds .env, parses KEY=value lines,
                # injects into os.environ — only if not already set
```

Order matters: `load_dotenv()` must run BEFORE any `os.getenv()` calls, or the file's values won't be there yet. Bonus: it returns `True`/`False` depending on whether it found a file — handy for "loaded from .env" vs "no .env found" messages.

(Install name has a hyphen — `pip install python-dotenv` — import name has an underscore — `from dotenv import ...`. Classic Python.)

### `print(..., file=sys.stderr)` — complaints go to the error channel

```
stdout → the program's RESULTS    ("Mode: Development")
stderr → the program's COMPLAINTS ("Error, missing configuration: ...")
```

The Unix-blessed separation: other programs can split the two streams (`> results.txt 2> errors.txt`), and warnings don't pollute the normal output. Related: `', '.join(list_of_names)` glues a list into one comma-separated string, perfect for readable messages.

## How the program flows

```
load_dotenv()                     .env fills the gaps (never overrides)
   ↓
load_config()        check the 5 required vars exist in os.environ:
                     MATRIX_MODE, DATABASE_URL, API_KEY, LOG_LEVEL, ZION_ENDPOINT
                     missing ones → warning on stderr, then CONTINUE with defaults
   ↓
MATRIX_MODE branch:
   "development" → show_dev()  (verbose: DEBUG logs, local sqlite, real URLs)
   "production"  → show_prod() (restrained: INFO logs, "Connected to...", "Online")
   anything else → warn on stderr, fall back to development
```

Note the design: `load_config()` **warns but never exits**. Missing config → stderr warning + defaults, program keeps going. That's what "handle missing configuration without crashing" looks like in practice.

## The three scenarios to try

```bash
# 1. zero configuration → defaults + warnings, no crash
rm -f .env && python3 ex1/oracle.py

# 2. with .env → values loaded from the file
cp .env.example .env && python3 ex1/oracle.py

# 3. shell override → environment beats .env
MATRIX_MODE=production API_KEY=secret123 python3 ex1/oracle.py
```

---

# Fun Facts / Interesting Questions 🤓

**What does a venv actually isolate — and what not?**
It isolates installed packages and the python binary selection. It does NOT isolate your files, the network, OS resources, or environment variables. It's a package-layer wall, not a container.

**Why choose Poetry over a plain requirements.txt?**
Reproducibility. pip resolves dependencies fresh at every install (two installs can differ); Poetry freezes the full resolution — including transitive dependencies — into `poetry.lock`, so every install is byte-identical, forever.

**Why `importlib.metadata` instead of just importing the package?**
It reads metadata from disk without executing any package code — a safe probe that works even when the package itself is broken.

**Why is an environment variable better than a constant in source code?**
Constants get committed to git and are visible to everyone, forever, in history. Env vars stay on the machine. Same spirit as the venv: containment.

**What is still NOT safe about environment variables?**
Any process on the machine can read another's environment; they leak into logs, crash reports, and error trackers; and a `.env` file on disk is readable by anyone with file access. Env vars are *better* than hardcoding — not *safe*.

**Why does the shell variable beat the `.env` file?**
`load_dotenv()`'s default behavior: never override existing variables. The ladder.

**Why does `.env.example` exist at all?**
It documents which variables the program needs without leaking values, and it powers the `cp` workflow.

**Why `sys.exit(1)` and not just `sys.exit()`?**
Exit codes are a language: 0 means success, non-zero means failure. Exiting with 0 on a failure path is telling the shell "all good" — a white lie that breaks scripts chaining commands with `&&`.

**Why raw strings (`r"..."`) for Windows paths?**
Backslashes are Python's escape character. `r` says "print them exactly as typed," so `matrix_env\Scripts\activate` survives intact instead of `\S` getting mangled.

---

# Quick-Reference Card 📇

```bash
# venv
python3 -m venv matrix_env
source matrix_env/bin/activate        # Windows: matrix_env\Scripts\activate
deactivate

# venv detection (construct.py)
sys.prefix != sys.base_prefix         # True = inside a venv

# dependency check without importing (loading.py)
importlib.metadata.version("pandas")  # → "2.1.0"

# configuration ladder (oracle.py)
load_dotenv()                                    # .env → os.environ (no overrides)
os.getenv("KEY", "default")                      # read politely

# secrets hygiene
# .env = real values, gitignored | .env.example = placeholders, committed

# streams
print("results")                     # stdout
print("problems", file=sys.stderr)   # stderr
```

---

# References

- Python `sys` module (executable, prefix, base_prefix, exit, stderr): https://docs.python.org/3/library/sys.html
- Python `os` module (getenv, environ): https://docs.python.org/3/library/os.html
- Python `os.path` (basename, dirname): https://docs.python.org/3/library/os.path.html
- Python `site` module (site-packages): https://docs.python.org/3/library/site.html
- `importlib.metadata` (installed package metadata): https://docs.python.org/3/library/importlib.metadata.html
- Python `venv` module: https://docs.python.org/3/library/venv.html
- pip user guide: https://pip.pypa.io/en/stable/user_guide/
- Poetry and pyproject.toml: https://python-poetry.org/docs/pyproject/
- pyproject.toml specification: https://packaging.python.org/en/latest/specifications/pyproject-toml/
- NumPy documentation: https://numpy.org/doc/stable/
- NumPy typing (`npt.NDArray`): https://numpy.org/doc/stable/reference/typing.html
- `numpy.random.choice`: https://numpy.org/doc/stable/reference/random/generated/numpy.random.choice.html
- pandas documentation: https://pandas.pydata.org/docs/
- pandas `DataFrame.plot`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html
- matplotlib pyplot: https://matplotlib.org/stable/api/pyplot.html
- matplotlib `pyplot.savefig`: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html
- python-dotenv: https://pypi.org/project/python-dotenv/
- SQLite (about): https://www.sqlite.org/about.html
- Raw strings: https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals
- `str.join`: https://docs.python.org/3/library/stdtypes.html#str.join
