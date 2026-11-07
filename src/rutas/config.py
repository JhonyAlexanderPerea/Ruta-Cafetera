from pathlib import Path

SEED = 42
TIME_LIMIT_S = 300  # límite de 5 minutos del protocolo
REPETITIONS = 5
UTM_EPSG = 32618  # UTM zona 18N

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
