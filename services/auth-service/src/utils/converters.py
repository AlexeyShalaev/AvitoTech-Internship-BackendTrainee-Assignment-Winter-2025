from typing import Any

from pydantic import BaseModel


def convert_sql_model_to_pydantic_schema(model: Any, schema: BaseModel) -> BaseModel:
    return schema(**model.__dict__)


def convert_sql_models_to_pydantic_schemas(
    models: iter, schema: BaseModel
) -> list[BaseModel]:
    return [convert_sql_model_to_pydantic_schema(row, schema) for row in models]


def convert_first_sql_model_in_array_to_pydantic_schema(
    models: list[Any] | None, schema: BaseModel
) -> BaseModel:
    if models and len(models) > 0:
        return convert_sql_model_to_pydantic_schema(models[0], schema)
    return schema()
