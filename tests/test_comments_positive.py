import allure
import pytest
from api.response_parser import ResponseParser
from utils.allure_helpers import (
    attach_db_result,
    attach_api_response,
)

@allure.title("TC-07: Создание комментария через API")
@allure.description("Проверяем создание комментария и его наличие в БД")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Comments")
@allure.story("CRUD")
def test_tc07_create_comment_positive(comments_client, db_client, create_test_post, comment_cleanup):
    post_id = create_test_post
    comment_data = {
        "post": post_id,
        "author_name": "Test User Adelia",
        "author_email": "test@example.com",
        "content": "Это тестовый комментарий SDET"
    }

    with allure.step("Отправить POST запрос на создание комментария"):
        response = comments_client.post(json=comment_data)
        attach_api_response(response, expected_status=201)
        assert response.status_code == 201

    comment_id = ResponseParser.get_id(response)
    comment_cleanup.append(comment_id)

    with allure.step(f"Проверить наличие комментария ID {comment_id} в БД"):
        result = db_client.get_comment_by_id(comment_id)
        attach_db_result(
            result=result,
            expected_values={"comment_post_ID": post_id, "comment_content": comment_data["content"]},
            name="Comment DB Check"
        )
        assert result is not None
        assert result["comment_post_ID"] == post_id
        assert comment_data["content"] in result["comment_content"]


@allure.title("TC-08: Редактирование комментария")
@allure.description("Проверяем изменение текста существующего комментария через API")
@allure.severity(allure.severity_level.NORMAL)
@allure.feature("Comments")
@allure.story("CRUD")
def test_tc08_update_comment_positive(comments_client, db_client, create_test_comment):
    comment_id = create_test_comment
    new_content = "Обновленный текст комментария TC008"

    with allure.step(f"Отправить POST запрос на обновление комментария ID {comment_id}"):
        response = comments_client.post(endpoint=f"{comment_id}", json={"content": new_content})
        attach_api_response(response, expected_status=200)
        assert response.status_code == 200

    with allure.step("Проверить изменения в БД"):
        result = db_client.get_comment_by_id(comment_id)
        assert new_content in result["comment_content"]


@allure.title("TC-09: Удаление комментария")
@allure.description("Проверяем полное удаление комментария через API")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Comments")
@allure.story("CRUD")
def test_tc09_delete_comment_positive(comments_client, db_client, create_test_comment):
    comment_id = create_test_comment

    with allure.step(f"Отправить DELETE запрос для комментария ID {comment_id}"):
        response = comments_client.delete(f"{comment_id}", params={"force": True})
        attach_api_response(response, expected_status=200)
        assert response.status_code == 200

    with allure.step("Проверить, что запись удалена из БД"):
        exists = db_client.check_comment_exists(comment_id)
        assert exists is False, f"Комментарий ID {comment_id} все еще существует в БД"