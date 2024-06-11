from functools import lru_cache

from fastapi import Depends

from auth.password_manager import get_password_manager
from core.config import settings
from core.utils import create_otp
from exceptions.user import UserServiceException
from models import Profile, User
from schemas import ConfirmEmailSchema, CreateUserSchema
from schemas.user import (
    ChangePasswordUserSchema,
    GetUserProfileSchema,
    UpdateUserSchema,
    UserImage,
)
from services.dataset import ensure_directory_exists
from services.email import get_email_service
from storages import BaseUserStorage, get_user_storage
from storages.base import BaseProfileStorage
from storages.profile import get_profile_storage

from .base import BaseUserService


class UserService(BaseUserService):

    def __init__(self, storage, profile_storage: BaseProfileStorage) -> None:
        self.storage = storage
        self.profile_storage = profile_storage
        self.path_file_storage = settings.FILE_STORAGE.PATH

    async def check_exist_email(self, email: str):
        if await self.storage.get_by_email(email):
            raise UserServiceException(
                "Пользователь с указанным адресом электронной почты уже существует."
            )

    async def check_exist_username(self, username: str):
        if await self.storage.get_by_username(username):
            raise UserServiceException(
                "Пользователь с указанным именем пользователя уже существует."
            )

    async def change_password(
        self, user_id: str, data: ChangePasswordUserSchema
    ):
        user = await self.storage.get_by_id(user_id)

        password_manager = get_password_manager()

        if not user or not password_manager.verify_password(
            password=data.current_password, hash_str=user.password_hash
        ):
            raise UserServiceException("Неверный текущий пароль")

        if data.new_password != data.confirm_new_password:
            raise UserServiceException("Введите 2 раза один и тот же пароль")

        new_hashed_password = password_manager.generate_hash(data.new_password)

        await self.storage.change_password(user_id, new_hashed_password)

    async def update(
        self, data: UpdateUserSchema, user_id: str
    ) -> GetUserProfileSchema:
        user = await self.storage.get_by_id(user_id)
        profile = await self.profile_storage.get_by_user_id(user_id=user_id)

        if not user or not profile:
            raise UserServiceException(
                "У данного пользователя не существует профиля."
            )
        if data.username and data.username != user.username:
            await self.check_exist_username(data.username)

        user_data = {"username": data.username}
        profile_data = {
            "full_name": data.full_name, 
            "phone_number": data.phone_number,
            }

        await self.profile_storage.update(user_id=user_id, data=profile_data)
        await self.storage.update(user_id=user_id, data=user_data)

        return GetUserProfileSchema(
            user_id=user_id,
            email=user.email,
            username=data.username,
            full_name=data.full_name,
            phone_number=data.phone_number,
            image=profile.image,
        )

    async def get_profile(self, user_id: str) -> GetUserProfileSchema:
        user = await self.storage.get_by_id(user_id)
        profile = await self.profile_storage.get_by_user_id(user_id=user_id)
        if not user or not profile:
            raise UserServiceException(
                "У данного пользователя не существует профиля."
            )
        return GetUserProfileSchema(
            user_id=user_id,
            email=user.email,
            username=user.username,
            full_name=profile.full_name,
            phone_number=profile.phone_number,
            image=profile.image,
        )

    async def upload_image(
        self, image: UserImage, user_id: str
    ) -> GetUserProfileSchema:
        self.validate_file_extension(image)

        user = await self.storage.get_by_id(user_id)
        profile = await self.profile_storage.get_by_user_id(user_id=user_id)

        if not user or not profile:
            raise UserServiceException(
                "У данного пользователя не существует профиля."
            )
        file_name = f"{user_id}.{image.filename.rsplit('.', 1)[1].lower()}"

        self.save_user_file(
            file=image,
            directory=f"{self.path_file_storage}/users_img",
            file_name=file_name,
        )
        path = f"users_img/{file_name}"
        await self.profile_storage.update(
            user_id=user_id, data={"image": path}
        )

        return GetUserProfileSchema(
            user_id=user_id,
            email=user.email,
            username=user.username,
            full_name=profile.full_name,
            phone_number=profile.phone_number,
            image=path,
        )

    async def create(self, data: CreateUserSchema):
        await self.check_exist_email(data.email)
        await self.check_exist_username(data.username)

        password_manager = get_password_manager()
        email_service = get_email_service()
        hashed_password = password_manager.generate_hash(data.password)
        otp_code = create_otp()

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hashed_password,
            otp_code=otp_code,
        )
        profile = Profile(
            user_id=user.id,
            full_name=data.full_name,
            phone_number=data.phone_number,
        )

        try:
            await self.storage.create_user_and_profile(
                user=user, profile=profile
            )
            await email_service.send_email_confirm(
                to=[
                    data.email,
                ],
                otp_code=otp_code,
            )
        except Exception as e:
            raise UserServiceException(
                "Ошибка при создании пользователя"
            ) from e

    async def confirm_email(self, data: ConfirmEmailSchema):
        user = await self.storage.get_by_email_and_otp(
            email=data.email, otp_code=data.otp_code
        )
        if not user:
            raise UserServiceException("Неверный код")
        await self.storage.activate_user(user_id=user.id)

    async def remove(self, user_id):
        await self.storage.delete_by_id(user_id=user_id)

    def validate_file_extension(self, file: UserImage):
        if not file.filename.endswith(".png") and not file.filename.endswith(
            ".jpg"
        ):
            raise UserServiceException(
                msg="Недопустимый тип файла. Разрешены только файлы формата png и jpg."
            )

    def save_user_file(self, file: UserImage, directory: str, file_name: str):
        ensure_directory_exists(directory=directory)

        path = f"{directory}/{file_name}"

        with open(path, "wb+") as file_object:
            file_object.write(file.file.read())

        return path


@lru_cache()
def get_user_service(
    storage: BaseUserStorage = Depends(get_user_storage),
    profile_storage: BaseProfileStorage = Depends(get_profile_storage),
) -> UserService:
    return UserService(storage=storage, profile_storage=profile_storage)
