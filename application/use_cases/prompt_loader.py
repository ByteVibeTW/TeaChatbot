from pathlib import Path

prompt_location = Path("template/prompt")


class PromptLoader:
    def __init__(self, file_name: str):
        self.file_name = prompt_location / file_name

    def load_prompt(self) -> str:
        with open(self.file_name, "r", encoding="utf-8") as file:
            prompt_template = file.read()
        return prompt_template
