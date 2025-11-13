import json 
from pathlib import Path 

class Localization:
    lang = "en" # By default;
    def __init__(self) : 
        self.translations = {}
        self.load_all()

    def load_all(self): 
        locales_dir = Path(__file__).parent.parent / "locales"
        for file in locales_dir.glob("*.json"):
            lang = file.stem  # 'en' или 'ru'
            with open(file, 'r', encoding='utf-8') as f:
                self.translations[lang] = json.load(f)
    
    def get(self, key, language):
        return self.translations.get(language, {}).get(key)

# Глобальный экземпляр
localization = Localization()