from infrastructure.db.mysql_db import MysqlDB


class CreateUserTempUseCase:
    def __init__(self, mysql_db: MysqlDB):
        self.mysql_db = mysql_db

    def execute(self, user_id: str, user_input: str, temp_data: dict) -> None:
        self.mysql_db.upsert_user_temp(
            user_id=user_id,
            user_question=user_input,
            questions=temp_data["questions"],
        )
