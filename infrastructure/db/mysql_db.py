import json
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class MysqlDB:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
    ):
        encoded_password = quote_plus(password)
        self.engine: Engine = create_engine(
            f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}",
            pool_pre_ping=True,
        )
        self._ensure_user_temp_table()
        self._ensure_system_init_state_table()

    def _ensure_user_temp_table(self) -> None:
        create_table_sql = text(
            """
            CREATE TABLE IF NOT EXISTS user_temp (
                user_id VARCHAR(255) PRIMARY KEY,
                user_question TEXT NOT NULL,
                questions JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        with self.engine.begin() as connection:
            connection.execute(create_table_sql)

    def _ensure_system_init_state_table(self) -> None:
        create_table_sql = text(
            """
            CREATE TABLE IF NOT EXISTS system_init_state (
                task_name VARCHAR(255) PRIMARY KEY,
                status VARCHAR(32) NOT NULL,
                details JSON NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        with self.engine.begin() as connection:
            connection.execute(create_table_sql)

    def upsert_user_temp(
        self, user_id: str, user_question: str, questions: list[dict]
    ) -> None:
        upsert_sql = text(
            """
            INSERT INTO user_temp (user_id, user_question, questions)
            VALUES (:user_id, :user_question, CAST(:questions AS JSON))
            ON DUPLICATE KEY UPDATE
                user_question = VALUES(user_question),
                questions = VALUES(questions),
                created_at = CURRENT_TIMESTAMP
            """
        )
        with self.engine.begin() as connection:
            connection.execute(
                upsert_sql,
                {
                    "user_id": user_id,
                    "user_question": user_question,
                    "questions": json.dumps(questions, ensure_ascii=False),
                },
            )

    def fetch_user_temp(self, user_id: str) -> dict | None:
        query_sql = text(
            """
            SELECT user_question, questions
            FROM user_temp
            WHERE user_id = :user_id
            LIMIT 1
            """
        )
        with self.engine.connect() as connection:
            row = connection.execute(query_sql, {"user_id": user_id}).mappings().first()

        if row is None:
            return None

        raw_questions = row["questions"]
        if isinstance(raw_questions, bytes):
            questions = json.loads(raw_questions.decode("utf-8"))
        elif isinstance(raw_questions, str):
            questions = json.loads(raw_questions)
        else:
            questions = raw_questions

        return {
            "userQuestion": row["user_question"],
            "questions": questions,
        }

    def is_init_completed(self, task_name: str) -> bool:
        query_sql = text(
            """
            SELECT status
            FROM system_init_state
            WHERE task_name = :task_name
            LIMIT 1
            """
        )
        with self.engine.connect() as connection:
            row = (
                connection.execute(query_sql, {"task_name": task_name})
                .mappings()
                .first()
            )
        return row is not None and row["status"] == "completed"

    def mark_init_completed(self, task_name: str, details: dict | None = None) -> None:
        upsert_sql = text(
            """
            INSERT INTO system_init_state (task_name, status, details)
            VALUES (:task_name, 'completed', CAST(:details AS JSON))
            ON DUPLICATE KEY UPDATE
                status = VALUES(status),
                details = VALUES(details),
                updated_at = CURRENT_TIMESTAMP
            """
        )
        with self.engine.begin() as connection:
            connection.execute(
                upsert_sql,
                {
                    "task_name": task_name,
                    "details": json.dumps(details or {}, ensure_ascii=False),
                },
            )
