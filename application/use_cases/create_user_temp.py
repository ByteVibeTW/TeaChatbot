from domain.services.temporary_file_service import TemporaryFileService


class CreateUserTempUseCase:
    """
    創建使用者暫存檔
    """

    def __init__(self, temp_file_name: str):
        self.temp_file_service = TemporaryFileService(temp_file_name)

    def execute(self, user_id: str, user_input: str, temp_data: dict):
        data = self.temp_file_service.load_temp_data()
        data[user_id] = {
            "user_question": user_input,
            "questions": temp_data["questions"],
        }
        self.temp_file_service.save_temp_data(data)
