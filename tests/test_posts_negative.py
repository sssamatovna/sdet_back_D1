import allure

from api.response_parser import ResponseParser
from db.queries import SQLQueries
from faker import Faker
from utils.allure_helpers import (
    attach_count_check,
    attach_db_result,
    attach_api_response,
)


@allure.title("TC-004: Создание поста через API без авторизации")
@allure.description("Проверяем, что API возвращает 401 и пост не создаётся в БД без авторизации")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Posts")
@allure.story("Security")
@allure.tag("negative", "api", "authorization")
def test_tc04_create_post_without_authorization(db_client, unauthorized_posts_client):
    fake = Faker()
    unique_title = fake.sentence()

    post_data = {
        "title": unique_title,
        "content": "Это тестовый контент, созданный с помощью API",
        "status": "publish",
    }

    with allure.step("Отправить POST запрос без авторизации"):
        response = unauthorized_posts_client.create_post(**post_data)
        attach_api_response(response, expected_status=401)

        assert (response.status_code == 401), f"Ожидался статус 401 Unauthorized, получен {response.status_code}"
        error_code = ResponseParser.get_error_code(response)

        assert (error_code == "rest_cannot_create"), f"Ожидался код ошибки 'rest_cannot_create', получено: '{error_code}'"

    with allure.step("Проверить, что пост НЕ создан в БД"):
        result = db_client.execute_query(
            SQLQueries.COUNT_POSTS_BY_TITLE, (unique_title,)
        )

        attach_count_check(
            entity=f"posts with title '{post_data['title']}'",
            expected_count=0,
            actual_count=result["post_count"],
        )

        assert (result["post_count"] == 0), f"Пост НЕ должен был быть создан! Найдено записей: {result['post_count']}"


@allure.title("TC-005: Обновление поста с невалидным статусом")
@allure.description("Проверяем, что API возвращает 4xx и статус поста не меняется в БД")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Posts")
@allure.story("Validation")
@allure.tag("negative", "api", "validation")
def test_tc05_update_post_with_invalid_status(
    posts_client, db_client, create_test_post
):
    post_id = create_test_post

    invalid_status = "invalid_status_xyz"

    with allure.step(f"Отправить PUT запрос с невалидным статусом '{invalid_status}'"):
        response = posts_client.update_post(post_id, {"status": invalid_status})

    with allure.step("Проверить HTTP Status(400 или 422) и код ошибки"):
        valid_status = [
            400,
            422,
        ]
        attach_api_response(response, expected_status=valid_status)
        assert (response.status_code in valid_status), f"Ожидался статус 400 или 422, получен {response.status_code}"

        error_code = ResponseParser.get_error_code(response)
        assert ("rest_invalid_param" in error_code), f"Ожидалась ошибка 'rest_invalid_param', получена '{error_code}'"

    with allure.step("Проверить, что post_status остался 'publish' в БД"):
        result = db_client.execute_query(SQLQueries.GET_POST_BY_ID, (post_id,))
        attach_db_result(
            result=result,
            expected_values={"post_status": "publish"},
            name="Post Status After Invalid Update",
        )

        assert result is not None, f"Пост ID={post_id} не найден в БД"
        assert (result["post_status"] == "publish"), f"Статус должен остаться 'publish', в БД: '{result['post_status']}'"


@allure.title("TC-006: Двойное удаление поста")
@allure.description("Проверяем идемпотентность DELETE - повторное удаление не должно вызывать ошибок")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Posts")
@allure.story("Idempotency")
@allure.tag("negative", "api", "idempotency")
def test_tc06_double_delete_post(posts_client, db_client, create_test_post):

    post_id = create_test_post

    with allure.step("Первичное удаление поста (в корзину)"):
        response_1 = posts_client.delete_post(post_id, force=False)
        attach_api_response(response_1, expected_status=200)
        assert (response_1.status_code == 200), f"Ожидался статус 200 OK, получен {response_1.status_code}"

    with allure.step("Проверка в БД после первого удаления"):
        result = db_client.execute_query(SQLQueries.GET_POST_BY_ID, (post_id,))

        attach_db_result(
            result=result,
            expected_values={"post_status": "trash"},
            name="Status After First Delete",
        )

        assert (result is not None and result["post_status"] == "trash"), f"Ожидался статус 'trash', в БД: '{result['post_status'] if result else None}'"

    with allure.step("Повторный запрос на удаление того же поста"):
        response_2 = posts_client.delete_post(post_id, force=False)
        valid_status = [200, 404, 410]
        attach_api_response(response_2, expected_status=valid_status)

        assert (response_2.status_code in valid_status), f"Ожидался статус 200/404/410, получен {response_2.status_code}"

    with allure.step("Финальная проверка БД (статус не изменился)"):
        result = db_client.execute_query(SQLQueries.GET_POST_BY_ID, (post_id,))

        attach_db_result(
            result=result,
            expected_values={"post_status": "trash"},
            name="Final Status Check",
        )

        assert (result is not None), f"Пост ID={post_id} не должен быть удалён физически из БД"
        assert (result["post_status"] == "trash"), f"Статус должен остаться 'trash', в БД: '{result['post_status']}'"