from supabase import Client, create_client


class PostgresqlDB:
    def __init__(self, db_url: str, db_key: str):
        self.client: Client = create_client(db_url, db_key)

    def insert_data(self, table_name: str, data: dict):
        self.client.table(table_name).insert(data).execute()

    def fetch_data(self, table_name: str, query: dict):
        response = self.client.table(table_name).select("*").filter(**query).execute()
        return response.data
