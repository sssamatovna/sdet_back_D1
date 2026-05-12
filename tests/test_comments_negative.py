import allure
import pytest
from api.response_parser import ResponseParser
from utils.allure_helpers import (
    attach_count_check,
    attach_api_response,
    attach_db_result
)


@allure.title("TC-10: Создание комментария без авторизации")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Comments")
@allure.story("Security")
def test_tc10_create_comment_unauthorized(unauth_comments_client, db_client, create_test_post):
    content = "Неавторизированный комментарий"
    payload = {
        "post": create_test_post,
        "author_name": "Unauth User",
        "author_email": "unauth@example.com",
        "content": content
    }

    with allure.step("Отправить запрос без заголовка Authorization"):
        response = unauth_comments_client.post(json=payload)
        attach_api_response(response, expected_status=401)
        # В зависимости от настроек WP может быть 401 или 403
        assert response.status_code in [401, 403]

    with allure.step("Проверить, что комментарий не появился в БД"):
        count = db_client.get_comment_count_by_content(content)
        attach_count_check("comments", 0, count)
        assert count == 0


@allure.title("TC-11: Обновление комментария с пустым контентом")
@allure.severity(allure.severity_level.NORMAL)
@allure.feature("Comments")
@allure.story("Validation")
def test_tc11_update_comment_empty_content(comments_client, db_client, create_test_comment):
    comment_id = create_test_comment

    with allure.step("Попытка обновить комментарий пустым текстом"):
        response = comments_client.post(endpoint=f"{comment_id}", json={"content": ""})
        attach_api_response(response, expected_status=400)
        assert response.status_code == 400

    with allure.step("Проверить, что текст в БД не изменился"):
        result = db_client.get_comment_by_id(comment_id)
        # Убеждаемся, что старый контент на месте
        assert "Initial Comment" in result["comment_content"]


@allure.title("TC-12: Двойное удаление комментария")
@allure.severity(allure.severity_level.NORMAL)
@allure.feature("Comments")
@allure.story("Idempotency")
def test_tc12_double_delete_comment(comments_client, create_test_comment):
    comment_id = create_test_comment

    with allure.step("Первое удаление"):
        res1 = comments_client.delete(f"{comment_id}", params={"force": True})
        assert res1.status_code == 200

    with allure.step("Второе удаление того же ID"):
        res2 = comments_client.delete(f"{comment_id}", params={"force": True})
        attach_api_response(res2, expected_status=404)
        # Обычно возвращается 404, так как объект уже удален физически
        assert res2.status_code == 404