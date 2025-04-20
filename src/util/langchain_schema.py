from typing_extensions import List, TypedDict

from langchain_core.prompt_values import ChatPromptValue
from src.util.output_schema import (
    ComponentIterateSchema,
    ComponentSchema,
    PromptImprovedIter,
    ValidPromptSchema,
    WireframeSchema,
    PromptImproved,
)
from src.util.api_schema import BaseTask


class designState(TypedDict):
    gemini_api_key: str
    model: str
    valid: bool
    user_prompt: str
    component_task: BaseTask
    context: str


class learnState(TypedDict):
    gemini_api_key: str
    user_prompt: str
    enhanced_prompt: PromptImproved
    design_plan: ComponentSchema
    comp_include: List
    wireframe: WireframeSchema
    component_task: BaseTask
    context: str


class genState(TypedDict):
    gemini_api_key: str
    model: str
    wireframe: WireframeSchema
    component_task: BaseTask
    context: str
    generatedCode: str
    history: ChatPromptValue
    new_prompt: str


class genStateIter(TypedDict):
    gemini_api_key: str
    model: str
    history: ChatPromptValue
    new_prompt: str
    enhance_prompt: PromptImprovedIter
    design_plan: ComponentIterateSchema
    generatedCode: str


class iterInputState(TypedDict):
    gemini_api_key: str
    history: ChatPromptValue
    new_prompt: str
