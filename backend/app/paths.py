from pathlib import Path
import os


def sample_root() -> Path:
    raw = os.environ.get("SAMPLE_ROOT")
    if raw:
        return Path(raw).resolve()
    here = Path(__file__).resolve()
    return (here.parents[2] / "samples" / "supply-chain").resolve()


def ontology_dir() -> Path:
    return sample_root() / "ontology"
