import os
import json
from google import genai
from google.genai import types
from src.util.output_schema import TsxOutput

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)


def generate(component_task, build_context, current_component_string, write_file=False):
    system_instruction2 = "You are an expert at writing React components.\nYour task is to write a new update for the provided React component for a web app, according to the provided task details with best practices of React.\nThe React component you write can make use of Tailwind classes for styling.\nUtilize the library components and icons as much as you can if provided.\n\nYou will write the full React component code, which should include all imports. Your generated code will be directly written to a .tsx React component file and used in production."

    generation_config_part2 = types.GenerateContentConfig(
        temperature=0.2,
        systemInstruction=system_instruction2,
        responseMimeType="application/json",
        responseSchema=TsxOutput,
    )
    gen_code_response = client.models.generate_content(
        model="gemini-2.5-pro-exp-03-25",
        config=generation_config_part2,
        contents=[
            build_context,
            f"- COMPONENT NAME : {component_task['name']}\n\n"
            + "- DESIRED COMPONENT CHANGES :\n```\n"
            + component_task["update"]["update_prompt"]
            + "\n```\n\n"
            + "- additional component update suggestions :\n```\n"
            + component_task["update"]["update_description"]
            + "\n```\n\n"
            + "- CURRENT COMPONENT CODE :"
            + current_component_string
            + "\n\nWrite the full code for the updated React web component, which uses Tailwind classes if needed (add tailwind dark: classes too if you can; backgrounds in dark: classes should be black), and, library components and icons, based on the provided design task.\n"
            + "When using flexbox, use the `gap` property instead of `space-x`\n"
            + "The full code of the new React component that you write will be written directly to a .tsx file inside the React project. Make sure all necessary imports are done, and that your full code is enclosed with ```tsx blocks.\n"
            # + "Answer with generated code only. DO NOT ADD ANY EXTRA TEXT DESCRIPTION OR COMMENTS BESIDES THE CODE. Your answer contains code only ! component code only !\nImportant :\n"
            + "- Make sure you import provided components libraries and icons that are provided to you if you use them !\n"
            + "- Tailwind classes should be written directly in the elements class tags (or className in case of React). DO NOT WRITE ANY CSS OUTSIDE OF CLASSES. DO NOT USE ANY <style> IN THE CODE ! CLASSES STYLING ONLY !\n"
            + "- Do not use libraries or imports except what is provided in this task; otherwise it would crash the component because not installed.\n"
            + "- Do not import extra libraries besides what is provided above and available in current component code!\n"
            + "- DO NOT HAVE ANY DYNAMIC DATA OR DATA PROPS ! Components are meant to be working as is without supplying any variable to them when importing them ! Only write a component that render directly with placeholders as data, component not supplied with any dynamic data.\n"
            + "- DO NOT HAVE ANY DYNAMIC DATA OR DATA PROPS !\n- Use picsum.photos for placeholder images\n"
            + "- DO NOT GENERATE SVG !\n"
            + "- Only write the code for the component; Do not write extra code to import it! The code will directly be stored in an individual React .tsx file !\n"
            + "- Very important : Your component should be exported as default !\n"
            + "Write the React component code as the React component genius you are - with the best ui formatting.\n",
        ],
    )

    generated_code = json.loads(gen_code_response.text)

    if write_file:
        with open(f"output/{component_task['name']}.tsx", "w+") as f:
            f.write(generated_code["tsx"].replace("```tsx\n", "").replace("\n```", ""))
        if os.getenv("WEB_LOCAL_MODULE_PATH"):
            with open(os.getenv("WEB_LOCAL_MODULE_PATH"), "w+") as f:
                f.write(
                    generated_code["tsx"].replace("```tsx\n", "").replace("\n```", "")
                )

    return generated_code["tsx"]
    # return gen_code_response.text

