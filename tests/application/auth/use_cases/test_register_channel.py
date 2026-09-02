from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.use_cases.register_channel import RegisterChannelUseCase
from app.application.common.interfaces.jwt import IJWTService
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.core.configs import Settings
from app.domain.channels.entities import Channel
from app.domain.channels.exceptions import ChannelWithEmailAlreadyExistsError, ChannelWithSlugAlreadyExistsError
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from tests.factories.commands.auth import RegisterChannelCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_register_channel_returns_correct_entity_if_created_and_activation_is_required(
    mock_container: AsyncContainer,
    test_settings: Settings,
):
    test_settings.auth_send_activation_email = True
    async with mock_container() as di:
        use_case = await di.get(RegisterChannelUseCase)
        session = await di.get(AsyncSession)
        pwd_hasher = await di.get(IPasswordHasher)
        jwt_service = await di.get(IJWTService)
        command = RegisterChannelCommandFactory.build()

        with patch.object(use_case._email_task_queue, 'send_channel_activation_code') as mock_email_task_queue:
            created_channel, tokens, is_activation_required = await use_case.execute(command=command)

        stmt = select(ChannelORM).where(ChannelORM.id == created_channel.id)
        result = await session.execute(statement=stmt)
        db_channel = result.scalar_one()

        assert is_activation_required

        mock_email_task_queue.assert_called_once()

        decoded_access_token = jwt_service.decode_access_token(token=tokens['access'])
        decoded_refresh_token = jwt_service.decode_refresh_token(token=tokens['refresh'])

        assert decoded_access_token['sub'] == created_channel.id
        assert decoded_access_token['token_type'] == 'access'
        assert decoded_refresh_token['sub'] == created_channel.id
        assert decoded_refresh_token['token_type'] == 'refresh'

        assert isinstance(created_channel, Channel)
        assert created_channel.email.value == command.email
        assert created_channel.name.value == command.name
        assert created_channel.slug.value == command.slug
        assert created_channel.description == command.description
        assert created_channel.country == command.country
        assert created_channel.avatar_s3_key is None
        assert not created_channel.is_active
        assert pwd_hasher.verify_password_hash(password=command.password, hash=created_channel.password_hash)

        assert db_channel.email == command.email
        assert db_channel.name == command.name
        assert db_channel.slug == command.slug
        assert db_channel.description == command.description
        assert db_channel.country == command.country
        assert db_channel.avatar_s3_key is None
        assert not db_channel.is_active
        assert pwd_hasher.verify_password_hash(password=command.password, hash=db_channel.password_hash)


@pytest.mark.asyncio
async def test_register_channel_returns_correct_entity_if_created_and_activation_is_not_required(
    mock_container: AsyncContainer,
    test_settings: Settings,
):
    test_settings.auth_send_activation_email = False
    async with mock_container() as di:
        use_case = await di.get(RegisterChannelUseCase)
        session = await di.get(AsyncSession)
        pwd_hasher = await di.get(IPasswordHasher)
        jwt_service = await di.get(IJWTService)
        command = RegisterChannelCommandFactory.build()

        with patch.object(use_case._email_task_queue, 'send_channel_activation_code') as mock_email_task_queue:
            created_channel, tokens, is_activation_required = await use_case.execute(command=command)

        stmt = select(ChannelORM).where(ChannelORM.id == created_channel.id)
        result = await session.execute(statement=stmt)
        db_channel = result.scalar_one()

        assert not is_activation_required

        mock_email_task_queue.assert_not_called()

        decoded_access_token = jwt_service.decode_access_token(token=tokens['access'])
        decoded_refresh_token = jwt_service.decode_refresh_token(token=tokens['refresh'])

        assert decoded_access_token['sub'] == created_channel.id
        assert decoded_access_token['token_type'] == 'access'
        assert decoded_refresh_token['sub'] == created_channel.id
        assert decoded_refresh_token['token_type'] == 'refresh'

        assert isinstance(created_channel, Channel)
        assert created_channel.email.value == command.email
        assert created_channel.name.value == command.name
        assert created_channel.slug.value == command.slug
        assert created_channel.description == command.description
        assert created_channel.country == command.country
        assert created_channel.avatar_s3_key is None
        assert created_channel.is_active
        assert pwd_hasher.verify_password_hash(password=command.password, hash=created_channel.password_hash)

        assert db_channel.email == command.email
        assert db_channel.name == command.name
        assert db_channel.slug == command.slug
        assert db_channel.description == command.description
        assert db_channel.country == command.country
        assert db_channel.avatar_s3_key is None
        assert db_channel.is_active
        assert pwd_hasher.verify_password_hash(password=command.password, hash=db_channel.password_hash)


@pytest.mark.asyncio
async def test_register_channel_raises_error_if_email_exists(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(RegisterChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session)
        command = RegisterChannelCommandFactory.build(email=db_channel.email)

        with pytest.raises(ChannelWithEmailAlreadyExistsError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_register_channel_raises_error_if_slug_exists(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(RegisterChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session)
        command = RegisterChannelCommandFactory.build(slug=db_channel.slug)

        with pytest.raises(ChannelWithSlugAlreadyExistsError):
            await use_case.execute(command=command)
