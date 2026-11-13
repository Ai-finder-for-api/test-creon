"""
Environment variables management and string interpolation.
Supports substituting {{VAR_NAME}} placeholders across URLs, headers, and payloads.
"""
import re
import json
from typing import Dict, Any, Optional


class EnvironmentManager:
    def __init__(self, initial_vars: Optional[Dict[str, str]] = None):
        self._vars: Dict[str, str] = initial_vars or {
            "BASE_URL": "http://127.0.0.1:8765",
            "API_KEY": "test-key-quantum-qa",
            "USER_ID": "usr_482910"
        }
        self._pattern = re.compile(r"\{\{([a-zA-Z0-9_\-\.]+)\}\}")

    def get_all(self) -> Dict[str, str]:
        return dict(self._vars)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self._vars.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._vars[key.strip()] = str(value)

    def remove(self, key: str) -> bool:
        if key in self._vars:
            del self._vars[key]
            return True
        return False

    def interpolate(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return text

        def replacer(match):
            var_name = match.group(1).strip()
            return self._vars.get(var_name, match.group(0))

        return self._pattern.sub(replacer, text)

    def interpolate_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        return {
            self.interpolate(k) or "": self.interpolate(v) or ""
            for k, v in data.items()
        }

    def export_json(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self._vars, f, indent=2)

    def import_json(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            if isinstance(loaded, dict):
                self._vars.update({str(k): str(v) for k, v in loaded.items()})
