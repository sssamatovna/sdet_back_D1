import json
from typing import Any, Optional, Union

import allure


def attach_api_response(
    response,
    expected_status: Union[int, list[int], None] = None,
    name: str = "API Response",
) -> None:
    """
    Прикрепляет детали API ответа к Allure отчёту.

    Args:
        response: requests.Response объект
        expected_status: Ожидаемый HTTP статус код
        name: Название вложения
    """
    from api.response_parser import ResponseParser

    details = [f"Status Code: {response.status_code}"]

    if expected_status is not None:
        if isinstance(expected_status, list):
            is_match = response.status_code in expected_status
        else:
            is_match = response.status_code == expected_status

        status_match = "MATCH" if is_match else "MISMATCH"
        details.append(f"Expected: {expected_status} ({status_match})")

    error_code = ResponseParser.get_error_code(response)
    if error_code:
        details.append(f"Error Code: {error_code}")
        details.append(f"Error Message: {ResponseParser.get_error_message(response)}")

    try:
        response_json = response.json()
        formatted_body = json.dumps(response_json, indent=4, ensure_ascii=False)
        details.append(f"\nResponse Body (JSON):\n{formatted_body}")
    except ValueError:
        text_body = response.text[:4000] + ("..." if len(response.text) > 4000 else "")
        details.append(f"\nResponse Body (Text):\n{text_body}")

    final_content = "\n".join(details)

    allure.attach(final_content, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_db_result(
    result: Optional[dict | list],
    expected_values: Optional[dict] = None,
    name: str = "DB Query Result",
) -> None:
    """Прикрепляет результат БД запроса к Allure отчёту."""
    if not result:
        allure.attach(
            "No data found in database",
            name=name,
            attachment_type=allure.attachment_type.TEXT,
        )
        return

    details = ""

    if isinstance(result, dict):
        details += "Database Record:\n"
        for key, value in result.items():
            if expected_values and key in expected_values:
                match = "MATCH" if value == expected_values[key] else "MISMATCH"
                details += f"  {key}: {value} ({match})\n"
            else:
                details += f"  {key}: {value}\n"

    elif isinstance(result, list):
        details += f"Database Records (count: {len(result)}):\n"
        for idx, record in enumerate(result[:5], 1):
            details += f"\nRecord {idx}:\n"
            for key, value in record.items():
                details += f"  {key}: {value}\n"
        if len(result) > 5:
            details += f"\n... and {len(result) - 5} more records"

    if expected_values:
        details += "\n\nExpected Values:\n"
        for key, value in expected_values.items():
            details += f"  {key}: {value}\n"

    allure.attach(details, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_validation_result(
    field: str,
    expected: Any,
    actual: Any,
    passed: Optional[bool] = None,
    name: Optional[str] = None,
) -> None:
    """Прикрепляет результат валидации поля к Allure отчёту."""
    if passed is None:
        passed = expected == actual

    status = "PASSED" if passed else "FAILED"

    details = f"Expected: {expected}\n" f"Actual: {actual}\n" f"\nValidation: {status}"

    if name is None:
        name = f"Validation: {field}"

    allure.attach(details, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_count_check(
    entity: str, expected_count: int, actual_count: int, name: Optional[str] = None
) -> None:
    """Прикрепляет результат проверки количества записей."""
    passed = expected_count == actual_count
    status = "PASSED" if passed else "FAILED"

    details = (
        f"Entity: {entity}\n"
        f"Expected Count: {expected_count}\n"
        f"Actual Count: {actual_count}\n"
        f"\nValidation: {status}"
    )

    if name is None:
        name = f"Count Check: {entity}"

    allure.attach(details, name=name, attachment_type=allure.attachment_type.TEXT)