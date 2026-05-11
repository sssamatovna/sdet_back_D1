from typing import Optional
import pymysql

class DBClient:
    """Клиент для выполнения SQL запросов к WordPress БД"""

    def __init__(self, connection: pymysql.Connection):
        self.connection = connection

    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = True):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()

    def get_comment_by_id(self, comment_id: int):
        query = "SELECT * FROM wp_comments WHERE comment_ID = %s"
        return self.execute_query(query, (comment_id,))

    def get_comment_count_by_content(self, content: str):
        query = "SELECT COUNT(*) as count FROM wp_comments WHERE comment_content LIKE %s"
        result = self.execute_query(query, (f"%{content}%",))
        return result['count'] if result else 0

    def check_comment_exists(self, comment_id: int) -> bool:
        query = "SELECT comment_ID FROM wp_comments WHERE comment_ID = %s"
        return self.execute_query(query, (comment_id,)) is not None