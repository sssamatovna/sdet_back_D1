import allure
import requests

from api.base_client import BaseAPIClient
from api.endpoints import APIEndpoints


class PostsClient(BaseAPIClient):
    """Клиент для управления постами WordPress"""

    @allure.step("Создание поста (POST /posts)")
    def create_post(
        self, title: str, content: str, status: str = "publish"
    ) -> requests.Response:
        post_data = {"title": title, "content": content, "status": status}
        return self.post(APIEndpoints.POSTS, json=post_data)

    @allure.step("Обновление поста (PUT /posts/{post_id})")
    def update_post(self, post_id: int, update_data: dict) -> requests.Response:
        endpoint = APIEndpoints.post_by_id(post_id)
        return self.put(endpoint, json=update_data)

    @allure.step("Удаление поста (DELETE /posts/{post_id})")
    def delete_post(self, post_id: int, force: bool = True) -> requests.Response:
        endpoint = APIEndpoints.post_by_id(post_id)
        params = {"force": "true"} if force else {}
        return self.delete(endpoint, params=params)

    @allure.step("Получение поста (GET /posts/{post_id})")
    def get_post(self, post_id: int) -> requests.Response:
        endpoint = APIEndpoints.post_by_id(post_id)
        return self.get(endpoint)