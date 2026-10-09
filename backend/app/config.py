from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================
# Application
# ============================================================

class ApplicationSettings(BaseModel):
    name: str = Field(default="AI Call Center Training Agent")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")


# ============================================================
# Database
# ============================================================

class DatabaseSettings(BaseModel):
    url: str


# ============================================================
# LiveKit
# ============================================================

class LiveKitSettings(BaseModel):
    url: str = ""
    api_key: str = ""
    api_secret: str = ""


# ============================================================
# LLM
# ============================================================

class LLMSettings(BaseModel):
    provider: str = ""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: float = 30.0
    api_key: str = ""


# ============================================================
# STT
# ============================================================

class STTSettings(BaseModel):
    provider: str = ""
    model: str = ""
    language: str = "en"
    api_key: str = ""


# ============================================================
# TTS
# ============================================================

class TTSSettings(BaseModel):
    provider: str = ""
    model: str = ""
    voice: str = ""
    language: str = "en"
    output_format: str = "pcm"
    api_key: str = ""


# ============================================================
# Storage
# ============================================================

class StorageSettings(BaseModel):
    provider: str = ""
    bucket: str = ""
    region: str = ""
    access_key: str = ""
    secret_key: str = ""


# ============================================================
# Telephony / SIP
# ============================================================

class TelephonySettings(BaseModel):
    provider: str = ""
    sip_username: str = ""
    sip_password: str = ""
    sip_host: str = ""
    outbound_caller_id: str = ""


# ============================================================
# Global Settings
# ============================================================

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    database_url: str = Field(
        validation_alias="DATABASE_URL",
    )

    # --------------------------------------------------------
    # LiveKit
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # LLM
    # --------------------------------------------------------

    llm_provider: str = Field(
        default="",
        validation_alias="LLM_PROVIDER",
    )

    llm_model: str = Field(
        default="",
        validation_alias="LLM_MODEL",
    )

    llm_temperature: float = Field(
        default=0.7,
        validation_alias="LLM_TEMPERATURE",
    )

    llm_max_tokens: int = Field(
        default=500,
        validation_alias="LLM_MAX_TOKENS",
    )

    llm_timeout: float = Field(
        default=30.0,
        validation_alias="LLM_TIMEOUT",
    )

    llm_api_key: str = Field(
        default="",
        validation_alias="LLM_API_KEY",
    )

    # --------------------------------------------------------
    # STT
    # --------------------------------------------------------

    stt_provider: str = Field(
        default="",
        validation_alias="STT_PROVIDER",
    )

    stt_model: str = Field(
        default="",
        validation_alias="STT_MODEL",
    )

    stt_language: str = Field(
        default="en",
        validation_alias="STT_LANGUAGE",
    )

    stt_api_key: str = Field(
        default="",
        validation_alias="STT_API_KEY",
    )

    # --------------------------------------------------------
    # TTS
    # --------------------------------------------------------

    tts_provider: str = Field(
        default="",
        validation_alias="TTS_PROVIDER",
    )

    tts_model: str = Field(
        default="",
        validation_alias="TTS_MODEL",
    )

    tts_voice: str = Field(
        default="",
        validation_alias="TTS_VOICE",
    )

    tts_language: str = Field(
        default="en",
        validation_alias="TTS_LANGUAGE",
    )

    tts_output_format: str = Field(
        default="pcm",
        validation_alias="TTS_OUTPUT_FORMAT",
    )

    tts_api_key: str = Field(
        default="",
        validation_alias="TTS_API_KEY",
    )

    turn_min_endpointing_delay: float = Field(
        default=0.5,
        validation_alias="TURN_MIN_ENDPOINTING_DELAY",
    )

    turn_max_endpointing_delay: float = Field(
        default=3.0,
        validation_alias="TURN_MAX_ENDPOINTING_DELAY",
    )

    turn_interruption_enabled: bool = Field(
        default=True,
        validation_alias="TURN_INTERRUPTION_ENABLED",
    )

    # --------------------------------------------------------
    # Storage
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Telephony / SIP
    # --------------------------------------------------------

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


# ============================================================
# Settings Instance
# ============================================================

settings = Settings()