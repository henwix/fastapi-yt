from unittest.mock import patch
from uuid import UUID

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.usecases import RegisterChannelWithEmailCodeUseCase
from app.application.common.dto.jwt import JWTTokens
from app.application.common.interfaces.security import IJWTService
from app.core.configs import Settings
from app.domain.channels.entities import Channel
from app.domain.channels.exceptions import ChannelEmailAlreadyExistsError, ChannelSlugAlreadyExistsError
from tests.factories.commands.auth import RegisterChannelWithEmailCodeCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_register_channel_with_email_code_returns_entity_if_created_and_activation_is_required(
    container: AsyncContainer,
    test_settings: Settings,
):
    test_settings.auth_send_activation_email = True
    async with container() as di:
        use_case = await di.get(RegisterChannelWithEmailCodeUseCase)
        jwt_service = await di.get(IJWTService)
        command = RegisterChannelWithEmailCodeCommandFactory.build()

        with patch.object(use_case._email_service, 'schedule_send_channel_activation_code') as email_service_mock:
            channel, tokens, activation_required = await use_case.execute(command=command)

        email_service_mock.assert_called_once()

        assert isinstance(channel, Channel)
        assert isinstance(channel.id, UUID)
        assert channel.email.to_raw() == command.email
        assert channel.name.to_raw() == command.name
        assert channel.slug.to_raw() == command.slug
        assert channel.description == command.description
        assert channel.country == command.country
        assert channel.password_hash is None
        assert not channel.is_active
        assert channel.avatar_s3_key is None

        assert isinstance(tokens, JWTTokens)
        decoded_access = jwt_service.decode_access_token(token=tokens.access.token)
        decoded_refresh = jwt_service.decode_refresh_token(token=tokens.refresh.token)

        assert decoded_access.jti is None
        assert decoded_access.token_type == 'access'
        assert decoded_access.sub == str(channel.id)

        assert decoded_refresh.jti is not None
        assert decoded_refresh.token_type == 'refresh'
        assert decoded_refresh.sub == str(channel.id)

        assert activation_required


@pytest.mark.asyncio
async def test_register_channel_with_email_code_returns_entity_if_created_and_activation_is_not_required(
    container: AsyncContainer,
    test_settings: Settings,
):
    test_settings.auth_send_activation_email = False
    async with container() as di:
        use_case = await di.get(RegisterChannelWithEmailCodeUseCase)
        jwt_service = await di.get(IJWTService)
        command = RegisterChannelWithEmailCodeCommandFactory.build()

        with patch.object(use_case._email_service, 'schedule_send_channel_activation_code') as email_service_mock:
            channel, tokens, activation_required = await use_case.execute(command=command)

        email_service_mock.assert_not_called()

        assert isinstance(channel, Channel)
        assert isinstance(channel.id, UUID)
        assert channel.email.to_raw() == command.email
        assert channel.name.to_raw() == command.name
        assert channel.slug.to_raw() == command.slug
        assert channel.description == command.description
        assert channel.country == command.country
        assert channel.password_hash is None
        assert channel.is_active
        assert channel.avatar_s3_key is None

        assert isinstance(tokens, JWTTokens)
        decoded_access = jwt_service.decode_access_token(token=tokens.access.token)
        decoded_refresh = jwt_service.decode_refresh_token(token=tokens.refresh.token)

        assert decoded_access.jti is None
        assert decoded_access.token_type == 'access'
        assert decoded_access.sub == str(channel.id)

        assert decoded_refresh.jti is not None
        assert decoded_refresh.token_type == 'refresh'
        assert decoded_refresh.sub == str(channel.id)

        assert not activation_required


@pytest.mark.asyncio
async def test_register_channel_with_email_code_raises_error_if_email_exists(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(RegisterChannelWithEmailCodeUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)

        command = RegisterChannelWithEmailCodeCommandFactory.build(email=channel.email)

        with pytest.raises(ChannelEmailAlreadyExistsError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_email == channel.email


@pytest.mark.asyncio
async def test_register_channel_with_email_code_raises_error_if_slug_exists(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(RegisterChannelWithEmailCodeUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)

        command = RegisterChannelWithEmailCodeCommandFactory.build(slug=channel.slug)

        with pytest.raises(ChannelSlugAlreadyExistsError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_slug == channel.slug
