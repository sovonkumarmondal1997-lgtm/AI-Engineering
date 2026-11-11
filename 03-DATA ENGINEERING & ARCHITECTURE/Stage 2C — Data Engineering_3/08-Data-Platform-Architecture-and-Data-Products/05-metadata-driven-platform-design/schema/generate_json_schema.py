from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from metadata_platform import PipelineSpec

out = Path(__file__).resolve().parent / "metadata-v3.schema.json"
out.write_text(json.dumps(PipelineSpec.model_json_schema(), indent=2) + "\n", encoding="utf-8")
print(out)
