from pathlib import Path
from typing import List, Dict, Any
import yaml


def load_yaml_list(path: Path) -> List[str]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [str(x).strip() for x in data if str(x).strip()]
    if isinstance(data, dict):
        return [str(v).strip() for v in data.values() if str(v).strip()]
    return []


def load_yaml_map(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data
    return {}
