from dishka import Provider, Scope, provide

from app.application.auth.usecases import (
    ActivateChannelUseCase,
    LoginWithEmailCodeConfirmUseCase,
    LoginWithEmailCodeUseCase,
    LoginWithPasswordUseCase,
    LogoutUseCase,
    RefreshJWTTokenUseCase,
    RegisterChannelWithEmailCodeUseCase,
    RegisterChannelWithPasswordUseCase,
    ResendChannelActivationCodeUseCase,
    ResetChannelPasswordConfirmUseCase,
    ResetChannelPasswordUseCase,
    SetChannelEmailConfirmUseCase,
    SetChannelEmailUseCase,
    SetChannelPasswordUseCase,
)
from app.application.channels.usecases import (
    ConfirmChannelAvatarUploadUseCase,
    DeleteChannelAvatarUseCase,
    DeleteChannelUseCase,
    GenerateChannelAvatarUploadUrlUseCase,
    GetChannelAboutInfoUseCase,
    GetChannelUseCase,
    UpdateChannelUseCase,
)
from app.application.common.usecases.email import (
    SendChannelActivationCodeUseCase,
    SendChannelResetPasswordCodeUseCase,
    SendChannelSetEmailCodeUseCase,
    SendLoginEmailCodeUseCase,
)
from app.application.common.usecases.s3 import AbortMultipartUploadUseCase, DeleteS3ObjectUseCase
from app.application.oauth.usecases import (
    DisconnectOAuthAccountUseCase,
    GenerateOAuthLoginUrlUseCase,
    GetOAuthConnectedAccountsUseCase,
    VerifyOAuthCodeUseCase,
)
from app.application.playlists.usecases import (
    AddVideoToPlaylistUseCase,
    CreatePlaylistUseCase,
    DeletePlaylistUseCase,
    DeleteVideoFromPlaylistUseCase,
    GetChannelPlaylistsUseCase,
    GetPersonalPlaylistsUseCase,
    GetPlaylistUseCase,
    GetPlaylistVideosUseCase,
    UpdatePlaylistUseCase,
)
from app.application.posts.usecases import (
    CreatePostCommentReactionUseCase,
    CreatePostCommentUseCase,
    CreatePostReactionUseCase,
    CreatePostUseCase,
    DeletePostCommentReactionUseCase,
    DeletePostCommentUseCase,
    DeletePostReactionUseCase,
    DeletePostUseCase,
    GetChannelPostsUseCase,
    GetPostCommentRepliesUseCase,
    GetPostCommentsUseCase,
    GetPostUseCase,
    UpdatePostCommentUseCase,
    UpdatePostUseCase,
)
from app.application.subscriptions.usecases import (
    GetSubscribersUseCase,
    GetSubscriptionsUseCase,
    SubscribeUseCase,
    UnsubscribeUseCase,
)
from app.application.videos.usecases import (
    AbortVideoMultipartUploadUseCase,
    AddVideoToHistoryUseCase,
    ClearVideoHistoryUseCase,
    CompleteVideoMultipartUploadUseCase,
    ConfirmVideoThumbnailUploadUseCase,
    CreateVideoCommentReactionUseCase,
    CreateVideoCommentUseCase,
    CreateVideoMultipartUploadUseCase,
    CreateVideoReactionUseCase,
    CreateVideoUseCase,
    CreateVideoViewUseCase,
    DeleteNotCompletedVideosUseCase,
    DeleteVideoCommentReactionUseCase,
    DeleteVideoCommentUseCase,
    DeleteVideoFromHistoryUseCase,
    DeleteVideoReactionUseCase,
    DeleteVideoThumbnailUseCase,
    DeleteVideoUseCase,
    GenerateVideoDownloadUrlUseCase,
    GenerateVideoPartUploadUrlUseCase,
    GenerateVideoThumbnailUploadUrlUseCase,
    GetChannelVideosUseCase,
    GetPersonalVideosUseCase,
    GetVideoCommentRepliesUseCase,
    GetVideoCommentsUseCase,
    GetVideoHistoryUseCase,
    GetVideoUseCase,
    UpdateVideoCommentUseCase,
    UpdateVideoUseCase,
)


class UseCasesProvider(Provider):
    scope = Scope.REQUEST

    # Channels
    get_channel = provide(GetChannelUseCase)
    get_channel_about_info = provide(GetChannelAboutInfoUseCase)
    update_channel = provide(UpdateChannelUseCase)
    delete_channel = provide(DeleteChannelUseCase)
    generate_channel_avatar_upload_url = provide(GenerateChannelAvatarUploadUrlUseCase)
    confirm_channel_avatar_upload = provide(ConfirmChannelAvatarUploadUseCase)
    delete_channel_avatar = provide(DeleteChannelAvatarUseCase)

    # Auth
    register_channel_with_password = provide(RegisterChannelWithPasswordUseCase)
    register_channel_with_email_code = provide(RegisterChannelWithEmailCodeUseCase)
    login_with_password = provide(LoginWithPasswordUseCase)
    login_with_email_code = provide(LoginWithEmailCodeUseCase)
    login_with_email_code_comfirm = provide(LoginWithEmailCodeConfirmUseCase)
    refresh_jwt_token = provide(RefreshJWTTokenUseCase)
    logout = provide(LogoutUseCase)
    activate_channel = provide(ActivateChannelUseCase)
    resend_channel_activation_code = provide(ResendChannelActivationCodeUseCase)
    set_channel_email = provide(SetChannelEmailUseCase)
    set_channel_email_confirm = provide(SetChannelEmailConfirmUseCase)
    set_channel_password = provide(SetChannelPasswordUseCase)
    reset_channel_password = provide(ResetChannelPasswordUseCase)
    reset_channel_password_confirm = provide(ResetChannelPasswordConfirmUseCase)

    # OAuth
    generate_oauth_login_url = provide(GenerateOAuthLoginUrlUseCase)
    verify_oauth_code = provide(VerifyOAuthCodeUseCase)
    get_oauth_connected_accounts = provide(GetOAuthConnectedAccountsUseCase)
    disconnect_oauth_account = provide(DisconnectOAuthAccountUseCase)

    # Videos
    create_video = provide(CreateVideoUseCase)
    delete_video = provide(DeleteVideoUseCase)
    update_video = provide(UpdateVideoUseCase)
    get_video = provide(GetVideoUseCase)
    get_personal_videos = provide(GetPersonalVideosUseCase)
    get_channel_videos = provide(GetChannelVideosUseCase)

    generate_video_thumbnail_upload_url = provide(GenerateVideoThumbnailUploadUrlUseCase)
    confirm_video_thumbnail_upload = provide(ConfirmVideoThumbnailUploadUseCase)
    delete_video_thumbnail = provide(DeleteVideoThumbnailUseCase)

    create_video_multipart_upload = provide(CreateVideoMultipartUploadUseCase)
    abort_video_multipart_upload = provide(AbortVideoMultipartUploadUseCase)
    generate_video_part_upload_url = provide(GenerateVideoPartUploadUrlUseCase)
    complete_video_multipart_upload = provide(CompleteVideoMultipartUploadUseCase)
    generate_video_download_url = provide(GenerateVideoDownloadUrlUseCase)

    delete_not_completed_videos = provide(DeleteNotCompletedVideosUseCase)

    # Video views
    create_video_view = provide(CreateVideoViewUseCase)

    # Video reactions
    create_video_reaction = provide(CreateVideoReactionUseCase)
    delete_video_reaction = provide(DeleteVideoReactionUseCase)

    # Video comment reactions
    create_video_comment_reaction = provide(CreateVideoCommentReactionUseCase)
    delete_video_comment_reaction = provide(DeleteVideoCommentReactionUseCase)

    # Video comments
    create_video_comment = provide(CreateVideoCommentUseCase)
    delete_video_comment = provide(DeleteVideoCommentUseCase)
    update_video_comment = provide(UpdateVideoCommentUseCase)
    get_video_comments = provide(GetVideoCommentsUseCase)
    get_video_comment_replies = provide(GetVideoCommentRepliesUseCase)

    # Video history
    add_video_to_history = provide(AddVideoToHistoryUseCase)
    delete_video_from_history = provide(DeleteVideoFromHistoryUseCase)
    clear_video_history = provide(ClearVideoHistoryUseCase)
    get_video_history = provide(GetVideoHistoryUseCase)

    # Playlists
    create_playlist = provide(CreatePlaylistUseCase)
    get_playlist = provide(GetPlaylistUseCase)
    get_playlist_videos = provide(GetPlaylistVideosUseCase)
    get_personal_playlists = provide(GetPersonalPlaylistsUseCase)
    get_channel_playlists = provide(GetChannelPlaylistsUseCase)
    delete_playlist = provide(DeletePlaylistUseCase)
    update_playlist = provide(UpdatePlaylistUseCase)
    add_video_to_playlist = provide(AddVideoToPlaylistUseCase)
    delete_video_from_playlist = provide(DeleteVideoFromPlaylistUseCase)

    # Posts
    create_post = provide(CreatePostUseCase)
    get_post = provide(GetPostUseCase)
    get_channel_posts = provide(GetChannelPostsUseCase)
    update_post = provide(UpdatePostUseCase)
    delete_post = provide(DeletePostUseCase)

    # Post reactions
    create_post_reaction = provide(CreatePostReactionUseCase)
    delete_post_reaction = provide(DeletePostReactionUseCase)

    # Post comments
    create_post_comment = provide(CreatePostCommentUseCase)
    delete_post_comment = provide(DeletePostCommentUseCase)
    update_post_comment = provide(UpdatePostCommentUseCase)
    get_post_comments = provide(GetPostCommentsUseCase)
    get_post_comment_replies = provide(GetPostCommentRepliesUseCase)

    # Post comment reactions
    create_post_comment_reaction = provide(CreatePostCommentReactionUseCase)
    delete_post_comment_reaction = provide(DeletePostCommentReactionUseCase)

    # Subscriptions
    subscribe = provide(SubscribeUseCase)
    unsubscribe = provide(UnsubscribeUseCase)
    get_subscribers = provide(GetSubscribersUseCase)
    get_subscriptions = provide(GetSubscriptionsUseCase)

    # Common/Email
    send_channel_activation_code = provide(SendChannelActivationCodeUseCase)
    send_channel_set_email_code = provide(SendChannelSetEmailCodeUseCase)
    send_channel_reset_password_code = provide(SendChannelResetPasswordCodeUseCase)
    send_login_email_code = provide(SendLoginEmailCodeUseCase)

    # Common/S3
    delete_s3_object = provide(DeleteS3ObjectUseCase)
    abort_multipart_upload = provide(AbortMultipartUploadUseCase)
