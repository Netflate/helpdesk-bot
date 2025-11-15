import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

class Localization:
    def __init__(self, default_lang: str = "en") -> None:
        self.default_lang = default_lang
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.load_all()

    def load_all(self) -> None:
        locales_dir = Path(__file__).parent.parent / "locales"
        self.translations.clear()
        for file in locales_dir.glob("*.json"):
            lang = file.stem
            with open(file, "r", encoding="utf-8") as f:
                self.translations[lang] = json.load(f)

    def available_languages(self) -> List[str]:
        return sorted(self.translations.keys())

    def _get_nested(self, data: Dict[str, Any], path: List[str]) -> Any:
        cur: Any = data
        for p in path:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return None
        return cur

    def get(self, key: Union[str, List[str]], language: Optional[str] = None, default: Any = None) -> Any:
        lang = language or self.default_lang
        path = key.split(".") if isinstance(key, str) else key

        val = self._get_nested(self.translations.get(lang, {}), path)
        if val is not None:
            return val

        if lang != self.default_lang:
            val = self._get_nested(self.translations.get(self.default_lang, {}), path)
            if val is not None:
                return val

        return default

    # Convenience-методы под вашу схему
    def categories(self, language: Optional[str] = None) -> Dict[str, Any]:
        return self.get("categories", language, default={}) or {}

    def category(self, category_id: str, language: Optional[str] = None) -> Dict[str, Any]:
        return self.get(["categories", category_id], language, default={}) or {}

    def category_display_name(self, category_id: str, language: Optional[str] = None) -> str:
        return self.get(["categories", category_id, "display_name"], language, default=category_id)

    def category_questions(self, category_id: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.get(["categories", category_id, "questions"], language, default=[]) or []

# Глобальный экземпляр
localization = Localization()