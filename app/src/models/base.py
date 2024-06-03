from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated


def check_object_id(value: Any) -> str:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid ObjectId")
    return str(value)


PydanticObjectId = Annotated[Any, AfterValidator(check_object_id)]


class BaseObjectIDModel(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PydanticObjectId: str},
    )


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)
