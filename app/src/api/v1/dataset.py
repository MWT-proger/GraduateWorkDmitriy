from fastapi import APIRouter, Depends, File, UploadFile

from auth.auth_bearer import JWTBearer
from schemas.auth import AuthJWTSchema
from schemas.dataset import DatasetSchema, ListDatasetsSchema
from services.base import BaseDatasetService
from services.dataset import get_dataset_service

router = APIRouter(
    tags=[
        "Dataset",
    ]
)


@router.post("/upload", response_model=DatasetSchema)
async def upload_dataset(
    dataset: UploadFile = File(...),
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseDatasetService = Depends(get_dataset_service),
):
    obj = await service.save_dataset(dataset, user_id=auth_data.user_id)

    return DatasetSchema(
        id=str(obj.id),
        file_name=obj.file_name,
        columns=obj.columns,
        created_at=obj.created_at,
    )


@router.get("/me", response_model=ListDatasetsSchema)
async def get_user_datasets(
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseDatasetService = Depends(get_dataset_service),
):
    result = await service.get_user_datasets(user_id=auth_data.user_id)
    data = []
    async for obj in result:
        data.append(
            DatasetSchema(
                id=str(obj.id),
                file_name=obj.file_name,
                columns=obj.columns,
                created_at=obj.created_at,
            )
        )
    return ListDatasetsSchema(data=data)
