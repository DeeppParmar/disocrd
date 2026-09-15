import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class I18nLoader:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self._cache: dict[str, dict[str, dict]] = {}
    
    def load(self, locale: str, namespace: str) -> dict:
        """Load a locale namespace file and cache it."""
        if locale not in self._cache:
            self._cache[locale] = {}
        
        if namespace in self._cache[locale]:
            return self._cache[locale][namespace]
        
        file_path = self.base_dir / locale / f"{namespace}.json"
        
        if not file_path.exists():
            if locale != "en":
                logger.warning(f"Locale file not found: {file_path}, falling back to 'en'")
                return self.load("en", namespace)
            else:
                logger.error(f"Base locale file not found: {file_path}")
                return {}
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._cache[locale][namespace] = data
                return data
        except Exception as e:
            logger.error(f"Failed to load locale file {file_path}: {e}")
            return {}

    def get(self, locale: str, namespace: str, key: str, **kwargs) -> str:
        """Get a translated string with variable interpolation."""
        data = self.load(locale, namespace)
        
        keys = key.split(".")
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                if locale != "en":
                    return self.get("en", namespace, key, **kwargs)
                return f"{namespace}:{key}"
        
        if isinstance(value, str):
            try:
                return value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing format key {e} in translation {namespace}:{key}")
                return value
            
        return f"{namespace}:{key}"

# Provide a default instance if needed, or instantiate properly in dependency injection
i18n = I18nLoader(Path(__file__).parent)
