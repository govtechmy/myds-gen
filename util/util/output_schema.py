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
