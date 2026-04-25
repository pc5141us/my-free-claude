from __future__ import annotations


"""Pydantic models for API responses."""

from typing import Union, Optional, Any, Literal

from pydantic import BaseModel

from .anthropic import ContentBlockText, ContentBlockThinking, ContentBlockToolUse


class TokenCountResponse(BaseModel):
    input_tokens: int


class ModelResponse(BaseModel):
    created_at: str
    display_name: str
    id: str
    type: Literal["model"] = "model"


class ModelsListResponse(BaseModel):
    data: list[ModelResponse]
    first_id: Optional[str]
    has_more: bool
    last_id: Optional[str]


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0


class MessagesResponse(BaseModel):
    id: str
    model: str
    role: Literal["assistant"] = "assistant"
    content: list[
        Union[ContentBlockText, Union[ContentBlockToolUse], Union[ContentBlockThinking], dict[str, Any], Any]
    ]
    type: Literal["message"] = "message"
    stop_reason: Optional[
        Literal["end_turn", "max_tokens", "stop_sequence", "tool_use"]
    ] = None
    stop_sequence: Optional[str] = None
    usage: Usage
