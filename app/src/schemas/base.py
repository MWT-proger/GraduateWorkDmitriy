from pydantic import BaseModel, Field

class SuccessSchema(BaseModel):
    msg: str = Field(example="Операция прошла успешно")