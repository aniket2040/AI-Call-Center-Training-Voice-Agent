from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseModel):
    name: str = Field(default="AI Call Center Training Agent")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")


class DatabaseSettings(BaseModel):
    url: str


class LiveKitSettings(BaseModel):
    url: str = ""
    api_key: str = ""
    api_secret: str = ""


class LLMSettings(BaseModel):
    provider: str = ""
    model: str = ""
    api_key: str = ""


class STTSettings(BaseModel):
    provider: str = ""
    model: str = ""
    api_key: str = ""


class TTSSettings(BaseModel):
    provider: str = ""
    model: str = ""
    api_key: str = ""


class StorageSettings(BaseModel):
    provider: str = ""
    bucket: str = ""
    region: str = ""
    access_key: str = ""
    secret_key: str = ""


class TelephonySettings(BaseModel):
    provider: str = ""
    sip_username: str = ""
    sip_password: str = ""
    sip_host: str = ""
    outbound_caller_id: str = ""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    app_name: str = Field(
        default="AI Call Center Training Agent",
        validation_alias="APP_NAME",
    )
    app_env: str = Field(
        default="development",
        validation_alias="APP_ENV",
    )
    debug: bool = Field(
        default=False,
        validation_alias="DEBUG",
    )
    log_level: str = Field(
        default="INFO",
        validation_alias="LOG_LEVEL",
    )

    database_url: str = Field(
        validation_alias="DATABASE_URL",
    )

    livekit_url: str = Field(
        default="",
        validation_alias="LIVEKIT_URL",
    )
    livekit_api_key: str = Field(
        default="",
        validation_alias="LIVEKIT_API_KEY",
    )
    livekit_api_secret: str = Field(
        default="",
        validation_alias="LIVEKIT_API_SECRET",
    )

    llm_provider: str = Field(
        default="",
        validation_alias="LLM_PROVIDER",
    )
    llm_model: str = Field(
        default="",
        validation_alias="LLM_MODEL",
    )
    llm_api_key: str = Field(
        default="",
        validation_alias="LLM_API_KEY",
    )

    stt_provider: str = Field(
        default="",
        validation_alias="STT_PROVIDER",
    )
    stt_model: str = Field(
        default="",
        validation_alias="STT_MODEL",
    )
    stt_api_key: str = Field(
        default="",
        validation_alias="STT_API_KEY",
    )

    tts_provider: str = Field(
        default="",
        validation_alias="TTS_PROVIDER",
    )
    tts_model: str = Field(
        default="",
        validation_alias="TTS_MODEL",
    )
    tts_api_key: str = Field(
        default="",
        validation_alias="TTS_API_KEY",
    )

    storage_provider: str = Field(
        default="",
        validation_alias="STORAGE_PROVIDER",
    )
    storage_bucket: str = Field(
        default="",
        validation_alias="STORAGE_BUCKET",
    )
    storage_region: str = Field(
        default="",
        validation_alias="STORAGE_REGION",
    )
    storage_access_key: str = Field(
        default="",
        validation_alias="STORAGE_ACCESS_KEY",
    )
    storage_secret_key: str = Field(
        default="",
        validation_alias="STORAGE_SECRET_KEY",
    )

    sip_provider: str = Field(
        default="",
        validation_alias="SIP_PROVIDER",
    )
    sip_username: str = Field(
        default="",
        validation_alias="SIP_USERNAME",
    )
    sip_password: str = Field(
        default="",
        validation_alias="SIP_PASSWORD",
    )
    sip_host: str = Field(
        default="",
        validation_alias="SIP_HOST",
    )
    sip_outbound_caller_id: str = Field(
        default="",
        validation_alias="SIP_OUTBOUND_CALLER_ID",
    )


settings = Settings()