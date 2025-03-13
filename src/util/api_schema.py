from pydantic import BaseModel


class TaskDescription(BaseModel):
    user: str
    llm: str


class ComponentClass(BaseModel):
    name: str
    usage: str


class BaseTask(BaseModel):
    name: str
    description: TaskDescription
    icons: list
    components: list[ComponentClass]


class ComponentCode(BaseModel):
    tsx: str


class BaseContext(BaseModel):
    task: BaseTask
    wireframe: str


class ToGenerate(BaseModel):
    task: BaseTask
    context: str


class ToPlanIterate(BaseModel):
    task: BaseTask
    update_prompt: str
    wireframe: str
    tsx: str


class UpdateTask(BaseModel):
    update_prompt: str
    update_description: str
    icons: list
    components: list[ComponentClass]
    wireframe: bool


class BaseTaskWthUpdate(BaseModel):
    name: str
    description: TaskDescription
    icons: list
    components: list[ComponentClass]
    update: UpdateTask


class ContextIterate(BaseModel):
    task: BaseTaskWthUpdate
    wireframe: str


class GenIterate(BaseModel):
    task: BaseTaskWthUpdate
    context: str
    tsx: str
