from pydantic import BaseModel
from typing import List, Optional


class LibraryComponent(BaseModel):
    library_component_name: str
    library_component_usage_reason: str


# class not_in_libraryComponent(BaseModel):
#     not_in_library_component_name: str
#     not_in_library_component_usage_reason: str


class NewComponentIconsElements(BaseModel):
    does_new_component_need_icons_elements: bool
    if_so_what_new_component_icons_elements_are_needed: Optional[List[str]] = None


class ComponentSchema(BaseModel):
    new_component_name: str
    new_component_description: str
    new_component_icons_elements: NewComponentIconsElements
    use_library_components: List[LibraryComponent]
    # use_not_in_library_components: Optional[List[not_in_libraryComponent]]


class ValidPromptSchema(BaseModel):
    valid_prompt: bool


class WireframeSchema(BaseModel):
    ascii_wireframe: str


class LibraryComponentIterate(BaseModel):
    does_update_need_new_library_components: bool
    if_so_what_library_components_should_be_included: Optional[List[LibraryComponent]] = None

# class IterStep(BaseModel):
#     step_num: int
#     name: str
#     detailed_instructions: str
class ComponentIterateSchema(BaseModel):
    description_of_update: str
    new_component_icons_elements: NewComponentIconsElements
    new_library_components: LibraryComponentIterate
    wireframe_need_to_be_updated: bool
    ascii_wireframe: str
    # steps: List[IterStep]


class TsxOutput(BaseModel):
    tsx: str

class PromptImproved(BaseModel):
    improved_request: str
    components: List[LibraryComponent]

class PromptImprovedIter(BaseModel):
    improved_request: str
    additional_components: Optional[List[LibraryComponent]]