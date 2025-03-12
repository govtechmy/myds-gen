from tqdm import tqdm
from dotenv import load_dotenv
from .stages import (
    design,
    component_generation,
    build_context,
    generation_validation,
    design_iterate,
    component_generation_iterate,
)


class GenerateComponent:
    load_dotenv()

    def __init__(self, prompt):
        if not design.prompt_validation(prompt):
            raise ValueError(
                "Prompt provided was not valid. Please enter a prompt about a web component"
            )
        self.prompt = prompt

    def component_generation_new(self):
        p_bar = tqdm(range(5), colour="green")
        self.design_data = design.design_planning(self.prompt)
        self.component_task = build_context.gen_comp_task(self.prompt, self.design_data)
        p_bar.update()
        self.wireframe = design.design_layout(self.prompt, self.component_task)
        p_bar.update()
        self.full_context = build_context.generate(self.component_task, self.wireframe)
        p_bar.update()
        self.component_string = component_generation.generate(
            self.component_task, self.full_context, write_file=True
        )
        p_bar.update()
        self.file_name = self.component_task["name"]
        self.component_string = generation_validation.validate_full(
            self.component_string, self.file_name
        )
        p_bar.update()
        print(f"Component is saved as: output/{self.file_name}.tsx")

    def component_iteration(self, update_prompt):
        self.update_prompt = update_prompt
        self.design_data_iterate = design_iterate.design_update(
            self.update_prompt,
            self.component_string,
            self.wireframe,
            self.component_task,
        )
        self.component_task = build_context.gen_comp_task_iter(
            self.prompt, self.design_data_iterate, self.component_task
        )

        if self.component_task["update"]["wireframe"]:
            # print("iterate wireframe")
            self.wireframe = design_iterate.design_layout(
                self.component_task, self.wireframe
            )

        self.full_context_iter = build_context.generate_iter(
            self.component_task, self.wireframe
        )

        self.component_string = component_generation_iterate.generate(
            self.component_task, self.full_context_iter, self.component_string, write_file=True
        )
        self.file_name = self.component_task["name"]
        self.component_string = generation_validation.validate_full(
            self.component_string, self.file_name
        )
        print(f"Component `{self.file_name} is updated at: output/{self.file_name}.tsx")
