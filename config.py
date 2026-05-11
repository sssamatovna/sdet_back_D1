from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Конфигурация проекта с использованием Pydantic Settings
    Поддерживает загрузку из .env файла и валидацию типов
    """

    # WordPress & API credentials
    wp_base_url: str = Field(
        default="http://localhost:8000", description="The base URL WordPress."
    )
    wp_api_user: str = Field(default="Adelia.Ilyasova", description="The API user name.")
    wp_api_pass: str = Field(default="123-Test", description="The API user password.")

    # MySQL Database params
    db_host: str = Field(default="127.0.0.1", description="MySQL host.")
    db_port: int = Field(default=3306, description="MySQL port.", ge=1, le=65535)
    db_user: str = Field(default="wordpress", description="MySQL user name.")
    db_pass: str = Field(default="wordpress", description="MySQL user password.")
    db_name: str = Field(default="wordpress", description="MySQL database name.")

    # Tables used in test cases
    table_posts: str = Field(default="wp_posts", description="Posts table used in TC-01 - TC-06.")
    table_comments: str = Field(default="wp_comments", description="Comments table used in TC-07 - TC-12.")

    # Оставлено для совместимости/расширяемости
    table_users: str = Field(default="wp_users", description="Users table.")
    table_usermeta: str = Field(default="wp_usermeta", description="Usermeta table.")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    @property
    def api_posts_endpoint(self) -> str:
        """Эндпоинт для работы с постами"""
        # Если в WP включены "простые" ссылки, используется rest_route
        return f"{self.wp_base_url}/index.php?rest_route=/wp/v2/posts"

    @property
    def api_comments_endpoint(self) -> str:
        """Эндпоинт для работы с комментариями"""
        # Явно указано в TC-07
        return f"{self.wp_base_url}/index.php?rest_route=/wp/v2/comments"

    @property
    def db_connection_params(self) -> dict:
        """Словарь параметров для передачи в коннектор БД (например, pymysql)"""
        return {
            "host": self.db_host,
            "port": self.db_port,
            "user": self.db_user,
            "password": self.db_pass,
            "database": self.db_name,
        }


settings = Config()