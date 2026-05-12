import allure
import requests

from api.base_client import BaseAPIClient
from api.endpoints import APIEndpoints


class CommentsClient(BaseAPIClient):
    """Клиент для управления комментариями WordPress"""

    @allure.step("Создание комментария (POST /comments)")
    def create_comment(
            self, post_id: int, content: str, author_name: str = None, author_email: str = None
    ) -> requests.Response:
        comment_data = {
            "post": post_id,
            "content": content
        }
        if author_name:
            comment_data["author_name"] = author_name
        if author_email:
            comment_data["author_email"] = author_email

        return self.post(APIEndpoints.COMMENTS, json=comment_data)

    @allure.step("Обновление комментария (PUT /comments/{comment_id})")
    def update_comment(self, comment_id: int, update_data: dict) -> requests.Response:
        endpoint = APIEndpoints.comment_by_id(comment_id)
        return self.put(endpoint, json=update_data)

    @allure.step("Удаление комментария (DELETE /comments/{comment_id})")
    def delete_comment(self, comment_id: int, force: bool = True) -> requests.Response:
        endpoint = APIEndpoints.comment_by_id(comment_id)
        # Для комментариев force=true удаляет их навсегда, минуя корзину
        params = {"force": "true"} if force else {}
        return self.delete(endpoint, params=params)

    @allure.step("Получение комментария (GET /comments/{comment_id})")
    def get_comment(self, comment_id: int) -> requests.Response:
        endpoint = APIEndpoints.comment_by_id(comment_id)
        return self.get(endpoint)