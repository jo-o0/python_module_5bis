# The Codex — The Complete User Guide 🧪🔮⚗️💥

Your personal companion for the whole laboratory, ex0 through ex4. This guide explains everything every exercise does and why, written so you can bounce back to it whenever a concept gets foggy.

**The journey, in five rooms:**

- **ex0 — The Sealed Laboratory** 🧪: detect your Python environment, check your dependencies, run a small data pipeline
- **ex1 — The Oracle** 🔮: configure a program with environment variables and a `.env` file, secrets safely out of the code
- **ex2 — The Alembic** ⚗️: modules vs packages, and the gateway file (`__init__.py`) that decides what a package shows the world
- **ex3 — Distillation & Transmutation** 🧪→🪙: summoning code from distant files, with absolute vs relative imports
- **ex4 — Avoid the Explosion** 💥: two files that need each other — and why only one pair survives

**Two golden rules that run through everything:**

1. Never modify `sys.path` — learn the import machinery, don't hack around it
2. ex0/ex1 use external libraries; ex2–ex4 use **only the files you wrote yourself** — just your own modules and packages, connected through imports

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

One venv covers the whole project. And never commit `matrix_env/` to git: anyone can recreate it in seconds with the commands above, which is exactly the point.

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

# ex2, ex3 & ex4 — The Formula Rooms ⚗️🧪💥

Welcome to the second half of the laboratory, where the formulas get written. From here on: **everything you import is a file you wrote yourself.** No external libraries, no standard library imports — just your own modules and packages, connected through imports. (That's the point: learning the import machinery with nothing else in the way.)

## The Big Idea First: Module vs Package 🏠

Everything in these three exercises hangs on one distinction:

```
MODULE:   one .py file                  elements.py
          ↓ you import it:              import elements

PACKAGE:  a folder of modules           alchemy/
          + an __init__.py                 ├── __init__.py   ← THE GATEWAY
          ↓ you import it:                ├── elements.py
          import alchemy                   ├── potions.py
                                           ├── transmutation/   ← subpackage
                                           └── grimoire/        ← subpackage
```

A folder is just a folder. The **`__init__.py`** file is what transforms it into a package — it's the file Python executes when you `import alchemy`, and it's where you decide the package's **public interface**.

---

# ex2 — The Alembic ⚗️

The lab is sealed, stocked, configured. Time to write formulas. Every alchemist starts with simple ingredients — some close at hand, some deep inside a cupboard. This exercise is about reaching each of them, and about the gateway that decides what a package shows the outside world.

**Files involved:**

| file | job |
|---|---|
| `elements.py` (root) | the close-at-hand module: `create_fire()`, `create_water()` |
| `alchemy/elements.py` | inside the cupboard: `create_earth()`, `create_air()` |
| `alchemy/__init__.py` | the gateway — curates what `import alchemy` exposes |
| `ft_alembic_0.py` | test: reach the root module directly |
| `ft_alembic_1.py` | test: go through the package interface |

## The gateway in your code

```python
# alchemy/__init__.py
from alchemy.elements import create_air
from alchemy.potions import strength_potion
from alchemy.potions import healing_potion as heal
```

Three names bound, one of them renamed (`healing_potion as heal` — `as` works in imports too, letting the package rebrand a function). Notice what is NOT there: `create_earth`.

## What `import alchemy` actually does

```
import alchemy
   ↓
Python runs alchemy/__init__.py  (top to bottom)
   ↓
Every name bound during that execution becomes an ATTRIBUTE
of the alchemy module object
```

Think of it as a storefront:

```
        import alchemy hands you this:
        ┌─────────────────────────────────┐
        │  alchemy                        │
        │  ├── create_air        ✨       │  ← bound in __init__.py
        │  ├── strength_potion   ✨       │  ← bound in __init__.py
        │  └── heal              ✨       │  ← bound in __init__.py
        │                                 │
        │  create_earth?  NOT on the      │
        │  shelf — but it EXISTS in the   │
        │  stockroom (alchemy.elements)   │
        └─────────────────────────────────┘
```

## The famous question: what did `__init__.py` change?

`alchemy/elements.py` defines `create_earth`, yet calling `alchemy.create_earth()` fails. **Nothing was hidden, nothing was made private.** So what changed?

**The namespace of the package object — nothing else.** The file `elements.py` is untouched, the function still exists, still callable. The `alchemy` module object simply has no attribute named `create_earth`, because attribute lookup on a module searches its own namespace, and `__init__.py` is the only file that decides what goes in there.

The proof that nothing is hidden — the side doors still work:

```python
import alchemy.elements              # go through the submodule
alchemy.elements.create_earth()      # ✅ "Earth element created"

from alchemy.elements import create_earth
create_earth()                       # ✅ works too
```

The function was always there. `import alchemy` just doesn't automatically load its submodules into the package namespace — Python only binds what `__init__.py` explicitly binds.

## The two test scripts, two ways of reaching

```python
# ft_alembic_0.py — reach a plain module directly (absolute import)
import elements
elements.create_fire()      # ✅ "Fire element created"

# ft_alembic_1.py — go THROUGH the package interface
import alchemy
alchemy.create_air()        # ✅ "Air element created"  (exposed by the gateway)
alchemy.create_earth()      # 💀 AttributeError: module 'alchemy' has no
                            #    attribute 'create_earth' — INTENTIONAL!
```

That AttributeError is the entire point of the exercise: proof that `__init__.py` defines the contract of the package. The test calls `create_earth` through the package interface precisely so the failure is visible. Python even helpfully suggests: `Did you mean: 'create_air'?` 💅

**One-line summary:** the gateway changes the namespace, not the code. `__init__.py` curates the public interface; it doesn't enforce privacy — there is no enforced privacy in Python, only convention (like `_leading_underscore` names).

---

# ex3 — Distillation and Transmutation 🧪→🪙

Summon distant code from distant files — first across modules, then one level deeper into a subpackage. Along the way, settle the ancient debate: absolute vs relative imports.

**Files involved:**

| file | job |
|---|---|
| `alchemy/potions.py` | brews potions from ALL FOUR elements — two of which live OUTSIDE the package |
| `alchemy/transmutation/recipes.py` | the gold recipe — uses at least one absolute and one relative import |
| `alchemy/transmutation/__init__.py` | the subpackage's own gateway, with `__all__` |
| `ft_distillation_0.py` | test: reach potions directly with `from...import` |
| `ft_transmutation_0.py` | test: reach the recipe through the subpackage path |

## Distillation: reaching outside the package

The potions need all four elements, but the lab's architecture splits them:

```
elements.py (root)          alchemy/elements.py
├── create_fire()  ─────┐   ├── create_earth()
└── create_water() ─────┤   └── create_air()
                        │           ↑
                        └───────────┘
                    potions.py needs BOTH sides
```

Two absolute imports, side by side, in `alchemy/potions.py`:

```python
import elements                # absolute: the ROOT module, via sys.path
import alchemy.elements        # absolute: inside the package tree

def healing_potion() -> str:
    earth = alchemy.elements.create_earth()   # in-package elements
    air   = alchemy.elements.create_air()
    return f"Healing potion brewed with '{earth}' and '{air}'"

def strength_potion() -> str:
    fire  = elements.create_fire()            # root-level elements
    water = elements.create_water()
    return f"Strength potion brewed with '{fire}' and '{water}'"
```

Both are **absolute imports** — they start from the top (the root of `sys.path`) and spell out the full path. `import elements` works because the root `elements.py` sits where Python looks; `alchemy.elements` works because `alchemy` is a package on that same path.

The test reaches the potions directly:

```python
# ft_distillation_0.py — direct access with from...import
from alchemy.potions import strength_potion, healing_potion

strength_potion()   # "Strength potion brewed with 'Fire element created'
                    #  and 'Water element created'"
healing_potion()    # "Healing potion brewed with 'Earth element created'
                    #  and 'Air element created'"
```

## Transmutation: one level deeper, and the import debate

Now the recipe lives inside a **subpackage** (`alchemy/transmutation/`). `recipes.py` deliberately uses **both** styles:

```python
from ..elements import create_air           # RELATIVE: up one level, into alchemy/
from elements import create_fire           # ABSOLUTE: from the root
from alchemy.potions import strength_potion  # ABSOLUTE: fully spelled out

def lead_to_gold() -> str:
    header: str = "Recipe transmuting Lead to Gold: "
    brew: str = f"brew '{create_air()}' and '{strength_potion()}'"
    mix: str = f"mixed with '{create_fire()}'"
    result: str = header + brew + mix
    return result
```

Notice the string-building: each piece carries its own trailing/leading spaces. Concatenating with `+` means YOU own every space — a missing one glues words together (`created''mixed`). Live-tested output:

```
Recipe transmuting Lead to Gold: brew 'Air element created' and 'Strength potion
brewed with 'Fire element created' and 'Water element created'' mixed with
'Fire element created'
```

### Absolute vs Relative — the debate, settled

```
ABSOLUTE:  from alchemy.potions import strength_potion
           └─ full path from the root. Explicit, unambiguous, means the same
              thing no matter which file it's written in. → DEFAULT choice.

RELATIVE:  from ..elements import create_air
           └─ position-based:  . = this package (current folder)
                               .. = parent package (one level up)
              Short and refactor-friendly INSIDE a package, cryptic outside.
```

**When to use which:**

| situation | choice | why |
|---|---|---|
| Crossing the package boundary (`from elements import create_fire`) | **absolute** | Survives the package being renamed/moved; explicit beats clever |
| Tight intra-package links that move together (`from ..elements import ...`) | **relative** | Compact; the relationship is fixed no matter what the package is called |
| Unsure? | **absolute** | The community default — absolute imports are recommended because they're usually more readable |

The test script reaches the recipe through the full subpackage path:

```python
# ft_transmutation_0.py
import alchemy.transmutation.recipes

alchemy.transmutation.recipes.lead_to_gold()
# → "Recipe transmuting Lead to Gold: brew 'Air element created' and ..."
```

**One-line summary:** absolute imports name a fixed location in the world (stable, explicit); relative imports name a location relative to home (compact, but silently wrong if the family moves). `recipes.py` shows both living together.

---

# ex4 — Avoid the Explosion 💥

The final mystery, the one that destroys laboratories: the **circular dependency** — two modules that try to summon each other in an endless loop. You write the same feature TWICE: the light grimoire (survives) and the dark grimoire (explodes). The difference between them is a single design decision, not a single line of syntax.

**Files involved:**

| file | job |
|---|---|
| `alchemy/grimoire/light_spellbook.py` | needs the validator to DECIDE |
| `alchemy/grimoire/light_validator.py` | needs the spellbook to KNOW what's allowed |
| `alchemy/grimoire/dark_spellbook.py` | same feature, written the naive way 💀 |
| `alchemy/grimoire/dark_validator.py` | ditto |
| `alchemy/grimoire/__init__.py` | exposes only the light API, with `__all__` |
| `ft_kaboom_0.py` | records a light spell — flawlessly ✅ |
| `ft_kaboom_1.py` | reaches the dark spellbook — the lab explodes 💥 |

## The problem shape

```
light_spellbook needs the validator to decide what's VALID
light_validator needs the spellbook to know what's ALLOWED
        ↓
each file needs the other = circular dependency
```

## How the light grimoire survives 🕊️ — function-level imports

The trick: **defer the import into the function body** instead of the top of the file.

```python
# light_spellbook.py
def light_spell_record(spell_name: str, ingredients: str) -> str:
    from .light_validator import validate_ingredients as validate   # ← INSIDE the function
    result: str = validate(ingredients)
    ...
```

```python
# light_validator.py
def validate_ingredients(ingredients: str) -> str:
    from .light_spellbook import light_spell_allowed_ingredients as allow  # ← INSIDE too
    ...
```

**The timeline:**

```
python3 ft_kaboom_0.py
   ↓ imports alchemy.grimoire → __init__.py → light_spellbook.py
   ↓ light_spellbook loads top-to-bottom... NO top-level import of validator
   ↓ module FULLY LOADED ✅  (nothing blocked it)
   ↓
   light_spell_record("Fantasy", "Earth, wind and fire") is CALLED
   ↓ NOW, for the first time, the validator import runs...
   ↓ validator loads → its own function-level import of light_spellbook
   ↓ light_spellbook is already in sys.modules, FINISHED → instant success ✨
   ↓ "Fantasy RECORDED"
```

**No cycle ever happens at load time, because neither module needs the other while it's still loading.** Python's `sys.modules` cache does the rest: by call time, both modules exist, so the function-level import is free.

## How the dark grimoire explodes 💀 — top-level mutual imports

Same feature, the naive way:

```python
# dark_spellbook.py — line 2, TOP LEVEL
from .dark_validator import validate_ingredients as validate

# dark_validator.py — line 2, TOP LEVEL
from .dark_spellbook import dark_spell_allowed_ingredients as allow
```

**The timeline of doom:**

```
python3 ft_kaboom_1.py
   ↓ imports dark_spellbook → starts loading it
   ↓ line 2: "from .dark_validator import ..." → starts loading validator
   ↓ validator line 2: "from .dark_spellbook import ..."
   ↓ dark_spellbook is IN sys.modules BUT STILL LOADING — a half-built shell
   ↓ the functions below line 2 DON'T EXIST YET
   ↓ 💥 ImportError: cannot import name 'dark_spell_allowed_ingredients'
        from partially initialized module (most likely due to a circular import)
```

## The key concept: "partially initialized module" 🧩

Python **starts executing a module the moment it's imported**, top to bottom. While it's mid-execution, the module object already exists in `sys.modules` — but it's hollow:

```
dark_spellbook loading, currently at line 2:
┌──────────────────────────────┐
│ module object: dark_spellbook│
│ namespace so far: {}          │  ← NOTHING defined yet!
│ (allowed_ingredients,        │
│  spell_record not born)       │
└──────────────────────────────┘
```

When the validator asks for `dark_spell_allowed_ingredients` from this shell, the name literally isn't there. Boom.

```
IMPORT TIME (loading the file)     CALL TIME (running a function)
─────────────────────────────      ──────────────────────────────
danger zone for cycles 💀          safe zone — everything's loaded ✨

dark grimoire imports here  →  💥    light grimoire imports here  →  ✅
```

The dark pair's explosion is **intentional** — it's the demonstration of the failure. `ft_kaboom_1.py` catches it and reports:

```python
try:
    from alchemy.grimoire.dark_spellbook import dark_spell_record
    ...
except Exception as e:
    print("...The lab has exploded lol\n", e)
```

## The validator logic (works for both grimoires)

```python
def validate_ingredients(ingredients: str) -> str:
    from .light_spellbook import light_spell_allowed_ingredients as allow
    allowed_list: list[str] = allow()
    user_ingredients: list[str] = [ing.strip().lower() for ing in ingredients.split(",")]
    for user_ing in user_ingredients:
        if user_ing in allowed_list:
            return f"{ingredients} VALID"
    return f"{ingredients} INVALID"    # ← AFTER the loop: only reject when
                                       #   EVERY ingredient failed
```

The subtle detail: the `INVALID` return sits **outside** the loop. Ingredients are valid if **at least one** of them is allowed — so you must check them ALL before rejecting. (A `return` inside the loop would reject based on the first ingredient alone — classic bug, and the reason `"wind, fire"` should be VALID because `fire` is allowed.)

Also note the ingredient normalization: `split(",")` → `strip()` → `lower()` — so `"Earth, wind and fire"` matches `"earth"` in the allowed list. Case-insensitive matching with clean spacing.

## The grimoire gateway, done right

```python
# alchemy/grimoire/__init__.py
from alchemy.grimoire.light_spellbook import (
    light_spell_record,
    light_spell_allowed_ingredients,
)

__all__ = ["light_spell_record", "light_spell_allowed_ingredients"]
```

`__all__` declares the public interface **explicitly**. It does double duty:

1. Tells linters "these imports are intentional — this IS the API" (silences the "unused import" grumbles flake8 raises on gateway files)
2. Controls what `from grimoire import *` brings in

And notice: only the **light** API is exposed. The dark spellbook is reachable only by going directly to its file — which is exactly what `ft_kaboom_1.py` does to trigger the explosion.

## Why does only ONE grimoire explode?

Both pairs are circular. The difference is **WHEN each pair asks for the other**: the light grimoire asks at **call time** (safe zone), the dark grimoire asks at **import time** (danger zone). Import time is where circular imports explode — because a module that's still loading can't answer questions about its own contents.

**One-line summary:** the light pair defers its cross-imports into function bodies, so no module needs the other while it's still loading; the dark pair imports at the top of both files, so the validator demands a name from a module that hasn't finished executing yet — partially initialized module, ImportError.

**Other ways to break a cycle** (if you ever need alternatives): merge the two files into one, extract the shared dependency into a third module both import, or pass the needed function as an argument (dependency injection).

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

**What exactly did `__init__.py` change, if nothing was hidden?**
It defines the package's namespace at import time: `import alchemy` executes `__init__.py`, and only the names bound there become attributes of the package. Privacy in Python is by convention (`_leading_underscore`), not enforcement — `create_earth` stays reachable through its submodule, just not through the front door.

**Why does `import alchemy` not give me `alchemy.elements` automatically?**
Python only binds what `__init__.py` explicitly binds. Submodules are loaded lazily — `alchemy.elements` becomes accessible after something imports it, but it never appears in the parent's namespace unless the gateway puts it there.

**Why does running a file directly break relative imports?**
`python3 file.py` gives the file no package context — Python doesn't know what "this package" (`.`) or "parent package" (`..`) mean. Hence `ImportError: attempted relative import with no known parent package`. Relative imports only make sense inside an imported package. (Workarounds like `python3 -m pkg.module` exist, but the real lesson: test scripts use absolute imports, package internals may use relative.)

**When should an alchemist use an absolute pathway, and when a relative one?**
Absolute for anything crossing the package boundary — it survives renames and moves. Relative for tight intra-package references where the relationship is fixed. When unsure, absolute — it's the community default because it's explicit and readable.

**Why does only one grimoire explode, when both pairs need each other?**
The light pair defers its cross-imports into function bodies, so neither module needs the other while still loading. The dark pair imports at the top of both files, so the validator hits a half-built module. Same circle, different timing → only one boom.

**What does "partially initialized module" mean?**
Python executes a module top-to-bottom at first import. A recursive import during that execution sees only the names defined so far — everything below the import line isn't born yet.

**Doesn't the light grimoire STILL have a circular dependency?**
Yes! Function-level imports don't remove the cycle — they delay it to call time, when both modules are fully loaded and `sys.modules` can answer instantly. It's a scheduling fix, not a structural one. The structural fixes: merge the modules, extract a shared third module, or inject the dependency as an argument.

**What's `__all__` actually for?**
Two jobs: it declares the public API explicitly (documentation + linters stop flagging gateway imports as "unused"), and it controls what `from package import *` brings in. Without it, star-imports grab every public name in the namespace.

**Why does `import elements` (root) work from inside `alchemy/potions.py`?**
Because `sys.path` still contains the directory you ran the script from (the repo root). Absolute imports resolve against `sys.path`, not against the importing file's location. Your imports reach "up and out" of the package for exactly this reason.

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

```python
# module vs package
elements.py                    # module — one file
alchemy/                       # package — folder + __init__.py
alchemy/transmutation/         # subpackage — a package inside a package

# the gateway (alchemy/__init__.py)
from alchemy.elements import create_air      # expose one name
from alchemy.potions import healing_potion as heal   # expose, renamed
__all__ = ["create_air", "strength_potion"]  # explicit public API

# absolute imports (from the root of sys.path)
import elements
import alchemy.elements
from alchemy.potions import healing_potion

# relative imports (inside a package only)
from .light_validator import validate_ingredients   # sibling
from ..elements import create_air                   # parent package

# circular dependency fix (light grimoire pattern)
def some_function() -> str:
    from .other_module import needed_thing          # defer to call time
    ...

# validator pattern — check ALL before rejecting
for item in candidates:
    if item in allowed:
        return f"{ingredients} VALID"
return f"{ingredients} INVALID"    # outside the loop!

# where Python caches loaded modules
sys.modules   # partially initialized during circular imports 💀
```

---

# References

## ex0/ex1 — environments & configuration

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

## ex2/ex3/ex4 — modules, packages & imports

- The import system (modules, packages, `__init__`, circular imports, `sys.modules`): https://docs.python.org/3/reference/import.html
- Packages (the tutorial version — very readable): https://docs.python.org/3/tutorial/modules.html#packages
- PEP 8 on imports (absolute vs relative recommendation): https://peps.python.org/pep-0008/#imports
- Intra-package references (relative imports in the docs): https://docs.python.org/3/reference/import.html#package-relative-imports
- Built-in functions: https://docs.python.org/3/library/functions.html
- Built-in types: https://docs.python.org/3/library/stdtypes.html
- flake8 (style checking): https://flake8.pycqa.org/
- mypy (type checking): https://mypy.readthedocs.io/
