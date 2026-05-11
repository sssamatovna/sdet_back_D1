import logging
from typing import Optional, Any
import requests

logger = logging.getLogger(__name__)

class ResponseParser:
    """Парсер JSON-ответов от WordPress API для тестов постов и комментариев"""

    @staticmethod
    def get_json(response: requests.Response) -> dict:
        """Безопасное извлечение JSON из ответа"""
        try:
            return response.json()
        except (ValueError, requests.exceptions.JSONDecodeError):
            logger.error(f"Failed to decode JSON from response: {response.text}")
            return {}

    @staticmethod
    def get_id(response: requests.Response) -> Optional[int]:
        """Извлекает ID ресурса (поста или комментария)"""
        return ResponseParser.get_json(response).get("id")

    @staticmethod
    def get_error_message(response: requests.Response) -> str:
        return ResponseParser.get_json(response).get("message", "")

    @staticmethod
    def get_error_code(response: requests.Response) -> str:
        """Извлекает код ошибки WordPress"""
        return ResponseParser.get_json(response).get("code", "")

    @staticmethod
    def get_status(response: requests.Response) -> Optional[str]:
        """Извлекает статус (publish, trash и т.д.)"""
        return ResponseParser.get_json(response).get("status")

    @staticmethod
    def get_field(response: requests.Response, field_name: str) -> Any:
        """Извлекает любое поле из ответа"""
        return ResponseParser.get_json(response).get(field_name)

    @staticmethod
    def is_deleted(response: requests.Response) -> bool:
        """
        Проверяет, содержит ли ответ подтверждение удаления.
        WordPress при удалении через API часто возвращает 'deleted': true.
        """
        return ResponseParser.get_json(response).get("deleted") is True

    @staticmethod
    def get_comment_post_id(response: requests.Response) -> Optional[int]:
        """Специфично для комментариев: к какому посту привязан"""
        return ResponseParser.get_json(response).get("post")

    @staticmethod
    def is_success(response: requests.Response) -> bool:
        """Проверка на успешный статус (2xx)"""
        return 200 <= response.status_code < 300
