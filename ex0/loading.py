import sys
import importlib.metadata
try:
    import numpy as np
    import numpy.typing as npt
    import pandas as pd
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    pass


def show_instructions() -> None:
    print("Use one of the options below:")
    print("* 'pip install -r requirements.txt' and run again")
    print("* 'poetry install' and 'poetry run python loading.py'")
    sys.exit()


def check_pandas() -> None:
    try:
        version = importlib.metadata.version("pandas")
        if version == "2.1.0":
            print("[OK] pandas (2.1.0) - Data manipulation ready")
        else:
            print(f"[KO] pandas version: {version}. Version '2.1.0' needed")
    except importlib.metadata.PackageNotFoundError:
        print("[KO] pandas package not found")
        show_instructions(0)


def check_numpy() -> None:
    try:
        version = importlib.metadata.version("numpy")
        if version == "1.25.0":
            print("[OK] numpy (1.25.0) - Numerical Computation ready")
        else:
            print(f"[KO] numpy version: {version}. Version '1.25.0' needed")
    except importlib.metadata.PackageNotFoundError:
        print("[KO] numpy package not found")
        show_instructions()


def check_matplotlib() -> None:
    try:
        version = importlib.metadata.version("matplotlib")
        if version == "3.7.2":
            print("[OK] matplotlib (3.7.2) - Visualization ready")
        else:
            print(f"[KO] matplotlib version: {version}. Version '3.7.2' needed")
    except importlib.metadata.PackageNotFoundError:
        print("[KO] matplotlib package not found")
        show_instructions()


def check_dependencies() -> None:
    check_pandas()
    check_numpy()
    check_matplotlib()


def main() -> None:
    print("\n* LOADING STATUS...LOADING PROGRAMS...\n")
    try:
        check_dependencies()
    except Exception:
        sys.exit(1)
    print("\nAnalyzing Matrix' Data...\n")
    matrix_data: npt.NDArray = np.sort(
        np.random.choice(2000, 1000, replace=False))
    print("Processing 1000 data points...\n")
    df: pd.DataFrame = pd.DataFrame({"matrix_data": matrix_data})
    print("\nVisualizing Matrix...\n")
    df.plot()
    print("...Analysis Complete...")
    file: str = "matrix_analysis.png"
    plt.savefig(file)
    print(f"Results saved to: {file}")


if __name__ == "__main__":
    main()
