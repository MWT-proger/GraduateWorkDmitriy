import os
from functools import lru_cache
from typing import List

from fastapi import Depends
from pandas import read_csv

from core.config import settings
from exceptions.dataset import DatasetServiceException
from models import Dataset
from schemas.dataset import DatasetFile
from storages import BaseDatasetStorage, get_dataset_storage

from .base import BaseDatasetService


class DatasetService(BaseDatasetService):
    def __init__(self, storage: BaseDatasetStorage) -> None:
        super().__init__(storage)
        self.path_file_storage = settings.FILE_STORAGE.PATH

    async def save_dataset(
        self, dataset_file: DatasetFile, user_id: str
    ) -> Dataset:
        self.validate_file_extension(dataset_file)

        new_dataset = Dataset(file_name=dataset_file.filename, user_id=user_id)

        path_save = self.save_user_file(
            file=dataset_file,
            directory=f"{self.path_file_storage}/{user_id}",
            file_name=f"{new_dataset.id}_{dataset_file.filename}",
        )

        new_dataset.file_path = path_save
        new_dataset.columns = self.get_columns_from_dataset_file(path_save)

        await self.storage.create_document(new_dataset)

        return new_dataset

    async def get_user_datasets(self, user_id: str) -> List[Dataset]:
        return await self.storage.get_documents_by_user(user_id=user_id)

    def validate_file_extension(self, file: DatasetFile):
        if not file.filename.endswith(".csv"):
            raise DatasetServiceException(
                msg="Недопустимый тип файла. Разрешены только файлы формата CSV."
            )

    def get_columns_from_dataset_file(self, path: str):
        df = read_csv(path)
        columns = list(df.columns)
        return columns

    def save_user_file(
        self, file: DatasetFile, directory: str, file_name: str
    ):
        ensure_directory_exists(directory=directory)

        path = f"{directory}/{file_name}"

        with open(path, "wb+") as file_object:
            file_object.write(file.file.read())

        return path


@lru_cache()
def get_dataset_service(
    storage: BaseDatasetStorage = Depends(get_dataset_storage),
) -> DatasetService:
    return DatasetService(storage=storage)


def ensure_directory_exists(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
