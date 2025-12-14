"""
Minimal skill loader for Rekindle MVP.
Loads skill templates and rules from JSON files.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"

class SkillLoader:
    """Load and access skill templates and rules."""

    def __init__(self):
        self._cache: Dict[str, Dict] = {}

    def list_skills(self) -> List[str]:
        """List available skills."""
        if not SKILLS_DIR.exists():
            return []
        return [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]

    def load_skill(self, skill_name: str) -> Dict[str, Any]:
        """Load skill data (templates, rules, etc)."""
        if skill_name in self._cache:
            return self._cache[skill_name]

        skill_dir = SKILLS_DIR / skill_name
        if not skill_dir.exists():
            raise ValueError(f"Skill not found: {skill_name}")

        skill_data = {}

        # Load all JSON files in skill directory
        for json_file in skill_dir.glob("*.json"):
            with open(json_file, 'r') as f:
                skill_data[json_file.stem] = json.load(f)

        # Load instructions if present
        inst_file = skill_dir / "instructions.md"
        if inst_file.exists():
            with open(inst_file, 'r') as f:
                skill_data['instructions'] = f.read()

        self._cache[skill_name] = skill_data
        return skill_data

    def get_template(self, skill_name: str, key: str, variant: int = 0) -> Optional[Dict]:
        """Get specific template from skill."""
        skill = self.load_skill(skill_name)

        # For opener_templates
        if 'templates' in skill:
            templates = skill['templates']
            if key in templates:
                variants = templates[key].get('variants', [])
                if variant < len(variants):
                    return variants[variant]
                # Return first variant as fallback
                return variants[0] if variants else None

        return None

    def get_rule(self, skill_name: str, key: str) -> Optional[Any]:
        """Get specific rule from skill."""
        skill = self.load_skill(skill_name)

        # Look in all loaded JSON files
        for data_key, data in skill.items():
            if data_key == 'instructions':
                continue
            if key in data:
                return data[key]
            # Support nested keys like "interested.send_qualifier"
            if '.' in key:
                parts = key.split('.')
                current = data
                try:
                    for part in parts:
                        current = current[part]
                    return current
                except (KeyError, TypeError):
                    continue

        return None

    def get_all_templates(self, skill_name: str, business_type: str = "generic") -> List[Dict]:
        """Get all template variants for a business type."""
        skill = self.load_skill(skill_name)

        if 'templates' in skill:
            templates_data = skill['templates']
            if business_type in templates_data:
                return templates_data[business_type].get('variants', [])
            # Fallback to generic
            if 'generic' in templates_data:
                return templates_data['generic'].get('variants', [])

        return []

    def fill_template(self, template: Dict, placeholders: Dict[str, str]) -> Dict[str, str]:
        """Fill template placeholders with actual values."""
        result = {}
        for key, value in template.items():
            if key == 'placeholders':
                continue
            if isinstance(value, str):
                # Replace all placeholders
                filled = value
                for ph_key, ph_value in placeholders.items():
                    filled = filled.replace(f"{{{ph_key}}}", str(ph_value))
                result[key] = filled
            else:
                result[key] = value
        return result


# Global instance
_loader = None

def get_loader() -> SkillLoader:
    """Get global skill loader instance."""
    global _loader
    if _loader is None:
        _loader = SkillLoader()
    return _loader
