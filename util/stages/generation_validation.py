import os 
from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

def validate(generated_code):
    system_instruction = """You are an expert at writing React components and fixing React code with errors.
Your task is to validate and ONLY fix the code of a React component for a web app if you identify any errors.
You will write the full React component code, which should include all imports.
The fixed code you generate will be directly written to a .tsx React component file and used directly in production."""

    generation_config_part2 = types.GenerateContentConfig(
        temperature=0.4,
        systemInstruction=system_instruction,
    )
    gen_code_response = client.models.generate_content(
        model="gemini-2.0-pro-exp-02-05",
        config=generation_config_part2,
        contents=[
            "The full code of the React web component:\n"
            + generated_code
            + "Make sure all necessary imports are done, and that your full code is enclosed with ```tsx ```"
            + "Answer with generated code only. DO NOT ADD ANY EXTRA TEXT DESCRIPTION OR COMMENTS BESIDES THE CODE. Your answer contains code only ! component code only !\n"
            + "Important :\n"
            + "- Make sure you import the components libraries and icons that are provided to you (if you use them) !\n"
            + "- Tailwind classes should be written directly in the elements class tags (or className in case of React). DO NOT WRITE ANY CSS OUTSIDE OF CLASSES\n"
            + "- Do not use libraries or imports except what is provided in this task; otherwise it would crash the component because not installed. Do not import extra libraries besides what is provided !\n"
            + "- Do not have ANY dynamic data! Components are meant to be working as is without supplying any variable to them when importing them ! Only write a component that render directly with placeholders as data, component not supplied with any dynamic data.\n"
            + "- You are allowed to remove any problematic part of the code and replace it\n"
            + "- Only write the code for the component; Do not write extra code to import it! The code will directly be stored in an individual React .tsx file"
        ],
    )

    return gen_code_response.text