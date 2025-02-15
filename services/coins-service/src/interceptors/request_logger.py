from typing import Any, Callable, Dict, List, Optional

import grpc
from grpc_interceptor import AsyncServerInterceptor
from loguru import logger


class RequestLogger(AsyncServerInterceptor):
    def __init__(
        self,
        log_headers: bool = True,
        log_method: bool = True,
        log_body: bool = False,
        custom_formatter: Optional[Callable[[Dict], str]] = None,
        excluded_headers: Optional[List[str]] = None,
    ):
        """
        :param log_headers: Логировать ли заголовки запроса
        :param log_method: Логировать ли название метода
        :param log_body: Логировать ли тело запроса
        :param custom_formatter: Пользовательская функция форматирования лога
        :param excluded_headers: Список заголовков, которые нужно исключить из логирования
        :param log_level: Уровень логирования (например, logging.INFO, logging.DEBUG)
        """
        self.log_headers = log_headers
        self.log_method = log_method
        self.log_body = log_body
        self.custom_formatter = custom_formatter
        self.excluded_headers = excluded_headers or []

    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ):
        log_data = {}

        if self.log_method:
            log_data["method"] = method_name

        if self.log_headers:
            metadata = context.invocation_metadata()
            headers = {k: v for k, v in metadata if k not in self.excluded_headers}
            log_data["headers"] = headers

        if self.log_body:
            log_data["body"] = str(request_or_iterator)

        # Если задан кастомный форматтер
        if self.custom_formatter:
            log_message = self.custom_formatter(log_data)
        else:
            log_message = self.default_formatter(log_data)

        logger.info(log_message)

        try:
            # Продолжаем выполнение запроса
            return await method(request_or_iterator, context)
        except Exception as e:
            logger.error(f"Error: {e}")
            raise

    def default_formatter(self, log_data: dict) -> str:
        """
        Форматирует лог по умолчанию.
        :param log_data: Данные для логирования
        :return: Отформатированная строка лога
        """
        return f"Request: {log_data}"
