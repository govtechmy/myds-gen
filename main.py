from rich.console import Console
from rich.markdown import Markdown
from tqdm import tqdm
from util.stages import design, component_generation, build_context, generation_validation

def main(prompt):
    
    valid_prompt = design.prompt_validation(prompt)

    if valid_prompt:
        p_bar = tqdm(range(4), colour="green")
        design_data = design.design_planning(prompt)
        p_bar.update()
        component_task, full_context = build_context.generate(prompt, design_data)
        p_bar.update()
        component_string = component_generation.generate(component_task,full_context)
        print(component_string)
        p_bar.update()
        component_string = generation_validation.validate(component_string)
        p_bar.update()
        return component_task["name"], component_string
    else:
        return None, False


if __name__ == "__main__":
    prompt = input("Describe your desired component: ")
    component_name, component_string = main(prompt)
    if component_string:
        console = Console()
        md = Markdown(component_string)
        console.print(md)

        with open(f"output/{component_name}.tsx", "w+") as f:
            f.write(component_string.replace("```tsx\n", "").replace(
                "\n```", ""
            ))
        print(f"Component is saved as: output/{component_name}.tsx" )
    else:
        print("Prompt provided was not valid. Please enter a prompt about a web component")