from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class BaseUUIDModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        
    )
