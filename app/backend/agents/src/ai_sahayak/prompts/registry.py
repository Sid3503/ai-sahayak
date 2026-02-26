import yaml
from pathlib import Path

class PromptRegistry:
    def __init__(self, prompt_dir: str):
        self.prompt_dir = Path(prompt_dir)

    def load_prompt(self, name: str, language: str = "en"):
        prompt_path = self.prompt_dir / f"{name}_{language}.yaml"
        if not prompt_path.exists():
            prompt_path = self.prompt_dir / f"{name}.yaml"
        
        with open(prompt_path, 'r') as f:
            return yaml.safe_load(f)
