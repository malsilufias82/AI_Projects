import json
from pathlib import Path
from typing import Dict, Optional

from app.ai.prompts.base import StringPromptTemplate
from app.core.logging import get_logger

logger = get_logger(__name__)

_PROMPTS_DIR = Path(__file__).parent / "templates"


class PromptLoader:
    """
    Loads prompt templates from the filesystem or a dict store.

    Template files live under app/ai/prompts/templates/ and follow
    the naming convention: {evaluator_id}.{prompt_name}.txt
    """

    def __init__(self, prompts_dir: Optional[Path] = None) -> None:
        self.prompts_dir = prompts_dir or _PROMPTS_DIR

    def load_from_file(self, template_id: str) -> StringPromptTemplate:
        """
        Load a .txt or .json template file by template_id.
        Raises FileNotFoundError if the template does not exist.
        """
        txt_path = self.prompts_dir / f"{template_id}.txt"
        json_path = self.prompts_dir / f"{template_id}.json"

        if txt_path.exists():
            content = txt_path.read_text(encoding="utf-8")
            logger.debug("prompt_loaded_from_txt", template_id=template_id)
            return StringPromptTemplate(template=content, template_id=template_id)

        if json_path.exists():
            data = json.loads(json_path.read_text(encoding="utf-8"))
            content = data.get("template", "")
            version = data.get("version", "1.0.0")
            logger.debug("prompt_loaded_from_json", template_id=template_id, version=version)
            return StringPromptTemplate(template=content, template_id=template_id, version=version)

        raise FileNotFoundError(f"No prompt template file found for '{template_id}'.")

    def load_from_dict(self, templates: Dict[str, str]) -> Dict[str, StringPromptTemplate]:
        """Bulk-load templates from an in-memory dict."""
        return {
            key: StringPromptTemplate(template=tmpl, template_id=key)
            for key, tmpl in templates.items()
        }
