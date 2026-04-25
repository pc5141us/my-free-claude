from __future__ import annotations


"""Pydantic models for Anthropic-compatible requests."""

from enum import Enum
class StrEnum(str, Enum):
    pass
from typing import Union, Optional, Any, Literal

from loguru import logger
from pydantic import BaseModel, field_validator, model_validator

from config.settings import Settings, get_settings


# =============================================================================
# Content Block Types
# =============================================================================
class Role(StrEnum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ContentBlockText(BaseModel):
    type: Literal["text"]
    text: str


class ContentBlockImage(BaseModel):
    type: Literal["image"]
    source: dict[str, Any]


class ContentBlockToolUse(BaseModel):
    type: Literal["tool_use"]
    id: str
    name: str
    input: dict[str, Any]


class ContentBlockToolResult(BaseModel):
    type: Literal["tool_result"]
    tool_use_id: str
    content: Union[str, Union[list[Any]], dict[str, Any], Any]


class ContentBlockThinking(BaseModel):
    type: Literal["thinking"]
    thinking: str


class SystemContent(BaseModel):
    type: Literal["text"]
    text: str


# =============================================================================
# Message Types
# =============================================================================
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: Union[
        str,
        list[
            Union[
                ContentBlockText,
                ContentBlockImage,
                ContentBlockToolUse,
                ContentBlockToolResult,
                ContentBlockThinking
            ]
        ]
    ]
    reasoning_content: Optional[str] = None


class Tool(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: dict[str, Any]


class ThinkingConfig(BaseModel):
    enabled: bool = True


# =============================================================================
# Request Models
# =============================================================================
class MessagesRequest(BaseModel):
    model: str
    max_tokens: Optional[int] = None
    messages: list[Message]
    system: Union[str, Optional[list[SystemContent]]] = None
    stop_sequences: Optional[list[str]] = None
    stream: Optional[bool] = True
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    metadata: dict[str, Optional[Any]] = None
    tools: Optional[list[Tool]] = None
    tool_choice: dict[str, Optional[Any]] = None
    thinking: Optional[ThinkingConfig] = None
    extra_body: dict[str, Optional[Any]] = None
    original_model: Optional[str] = None
    resolved_provider_model: Optional[str] = None

    @model_validator(mode="after")
    def map_model(self) -> MessagesRequest:
        """Map any Claude model name to the configured model (model-aware)."""
        settings = get_settings()
        if self.original_model is None:
            self.original_model = self.model

        resolved_full = settings.resolve_model(self.original_model)
        self.resolved_provider_model = resolved_full
        self.model = Settings.parse_model_name(resolved_full)

        if self.model != self.original_model:
            logger.debug(f"MODEL MAPPING: '{self.original_model}' -> '{self.model}'")

        return self


class TokenCountRequest(BaseModel):
    model: str
    messages: list[Message]
    system: Union[str, Optional[list[SystemContent]]] = None
    tools: Optional[list[Tool]] = None
    thinking: Optional[ThinkingConfig] = None
    tool_choice: dict[str, Optional[Any]] = None

    @field_validator("model")
    @classmethod
    def validate_model_field(cls, v: str, info) -> str:
        """Map any Claude model name to the configured model (model-aware)."""
        settings = get_settings()
        resolved_full = settings.resolve_model(v)
        return Settings.parse_model_name(resolved_full)
