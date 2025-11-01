import json
import os


class TemporaryFileService:
    """
    讀取與寫入暫存檔
    """

    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            try:
                with open(file_path, "w") as f:
                    json.dump({}, f, indent=4)
            except Exception as e:
                print(f"[TemporaryFileService] Error creating temp file: {e}")
        self.file_path = file_path

    def save_temp_data(self, data: dict):
        try:
            with open(self.file_path, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[TemporaryFileService] Error saving temp data: {e}")

    def load_temp_data(self) -> dict:
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[TemporaryFileService] Error loading temp data: {e}")
            return {}
