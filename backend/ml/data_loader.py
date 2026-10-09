from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def read_csv_safe(path: Path) -> pd.DataFrame:
    """
    Robust CSV reader for mixed real-world datasets.
    Tries common encodings without silently losing data.
    """

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1",
    ]

    last_error = None

    for encoding in encodings:
        try:
            df = pd.read_csv(
                path,
                encoding=encoding,
                encoding_errors="strict",
                low_memory=False,
            )

            print(f"[DATA] Loaded: {path.name} | encoding={encoding}")
            print(f"[DATA] Shape: {df.shape}")

            return df

        except UnicodeDecodeError as exc:
            last_error = exc

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"Unable to decode {path}. Last error: {last_error}",
    )


def load_glof_history() -> pd.DataFrame:
    path = DATA_DIR / "raw" / "glof_history.csv"
    return read_csv_safe(path)


def load_glacier_master() -> pd.DataFrame:
    path = DATA_DIR / "processed" / "glacier_master.csv"
    return read_csv_safe(path)


def load_rgi_clean() -> pd.DataFrame:
    path = DATA_DIR / "processed" / "rgi_v7_clean.csv"
    return read_csv_safe(path)


def load_rgi_analysis() -> pd.DataFrame:
    path = DATA_DIR / "processed" / "rgi_v7_analysis_records.csv"
    return read_csv_safe(path)


def discover_lake_csvs() -> list[Path]:
    locations = [
        DATA_DIR / "raw" / "glacial_lakes",
        DATA_DIR / "processed" / "glacial_lakes",
    ]

    files = []

    for directory in locations:
        if directory.exists():
            files.extend(directory.rglob("*.csv"))

    # remove duplicates
    return sorted(set(files))


def load_glacial_lakes() -> pd.DataFrame:
    files = discover_lake_csvs()

    if not files:
        raise FileNotFoundError(
            "No glacial lake CSV files found."
        )

    frames = []

    for file in files:
        try:
            df = read_csv_safe(file)
            df["source_file"] = file.name
            frames.append(df)
        except Exception as exc:
            print(f"[WARNING] Could not load {file}: {exc}")

    if not frames:
        raise RuntimeError("No glacial lake dataset could be loaded.")

    result = pd.concat(
        frames,
        ignore_index=True,
        sort=False,
    )

    result = result.drop_duplicates()

    print(
        f"[DATA] Combined glacial lake records: "
        f"{len(result):,}"
    )

    return result