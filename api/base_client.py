import json
import logging
import allure
import requests
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Базовый класс для работы с API WordPress"""

    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

    def _form_url(self, endpoint: str) -> str:
        """Формирует итоговый URL для WordPress REST API"""
        clean_endpoint = str(endpoint).strip('/')

        # Если эндпоинт пустой, возвращаем просто базовый URL
        if not clean_endpoint:
            return self.base_url

        if "rest_route=" in self.base_url:
            return f"{self.base_url}/{clean_endpoint}"

        # Для стандартных ЧПУ (Pretty Permalinks)
        return f"{self.base_url.rstrip('/')}/{clean_endpoint}"

    @staticmethod
    def _attach_to_allure(name: str, content: Any, attachment_type=allure.attachment_type.JSON):
        if content is not None:
            if isinstance(content, (dict, list)):
                content = json.dumps(content, indent=2, ensure_ascii=False)
            allure.attach(str(content), name=name, attachment_type=attachment_type)

    def _send_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Единый метод для отправки запросов, логирования и Allure-отчетов"""
        url = self._form_url(endpoint)

        # Логирование в консоль/файл
        logger.info(f"Request: {method} {url}")
        if kwargs.get("json"):
            logger.debug(f"Request Payload: {kwargs['json']}")

        with allure.step(f"API Request: {method} {endpoint}"):
            response = self.session.request(method=method, url=url, **kwargs)

            # Логируем ответ
            logger.info(f"Response Status: {response.status_code}")

            # Добавляем данные в Allure для удобного дебага
            self._attach_to_allure("Request URL", url, attachment_type=allure.attachment_type.TEXT)
            if kwargs.get("json"):
                self._attach_to_allure("Request Body", kwargs["json"])

            try:
                if response.text:
                    self._attach_to_allure("Response Body", response.json())
            except Exception:
                self._attach_to_allure("Response Body (Text)", response.text,
                                       attachment_type=allure.attachment_type.TEXT)

            return response

    def get(self, endpoint: str = "", **kwargs) -> requests.Response:
        return self._send_request("GET", endpoint, **kwargs)

    def post(self, endpoint: str = "", json: Optional[dict] = None, **kwargs) -> requests.Response:
        return self._send_request("POST", endpoint, json=json, **kwargs)

    def put(self, endpoint: str = "", json: Optional[dict] = None, **kwargs) -> requests.Response:
        return self._send_request("PUT", endpoint, json=json, **kwargs)

    def delete(self, endpoint: str = "", **kwargs) -> requests.Response:
        return self._send_request("DELETE", endpoint, **kwargs)
