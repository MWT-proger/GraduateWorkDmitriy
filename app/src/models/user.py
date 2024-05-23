from pydantic import BaseModel, ConfigDict, Field
from bson import ObjectId

class UserModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    email: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        
    )
