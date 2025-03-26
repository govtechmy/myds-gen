import json
import os
import re
import subprocess
from google import genai
from google.genai import types
from src.util.output_schema import TsxOutput

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

DEP_TYPE = os.getenv("DEP_TYPE")

if DEP_TYPE == "serverless":
    import requests

    DESIGN_DOC = os.environ["DESIGN_DOC"]
    COLOR_DOC = os.environ["COLOR_DOC"]


def validate_only_gemini(generated_code):
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


def get_error_line(line_number, file_name):
    with open(file_name) as f:
        data = f.readlines()

    return data[int(line_number) - 1].strip()


def validate_lint(file_name):
    result = subprocess.run(
        ["npx", "eslint", "--fix", file_name, "--format", "json"],
        capture_output=True,
        text=True,  # Decode bytes to string
        check=False,
    )
    errors = [
        f"line {i['line']}: `{get_error_line(i['line'], file_name)}`\n- eslint error on line {i['line']}:\n  `{i['ruleId']}: {i['message']}`"
        for i in json.loads(result.stdout)[0]["messages"]
    ]
    return errors


def validate_tsc(file_name):
    result = subprocess.run(
        [
            "tsc",
            file_name,
            "--target",
            "es5",
            "--lib",
            "dom,dom.iterable,esnext",
            "--allowJs",
            "--skipLibCheck",
            "--strict",
            "--noEmit",
            "--esModuleInterop",
            "--module",
            "esnext",
            "--moduleResolution",
            "bundler",
            "--resolveJsonModule",
            "--isolatedModules",
            "--jsx",
            "preserve",
            "--noEmit",
        ],
        capture_output=True,
        text=True,  # Decode bytes to string
        check=False,
    )
    errors = list(
        set(
            [
                f"line {i}: `{get_error_line(i, file_name)}`\n- tsc error on line {i}:\n  `{x.strip()}`"
                for i, x in zip(
                    re.findall(r"\((\d+?),\d+?\):", result.stdout),
                    re.findall(r":([\s\S]+?)\n", result.stdout),
                )
            ]
        )
    )
    print(errors)
    return errors


def fix_code_gemini(error_text, generated_code, file_name):
    if DEP_TYPE == "serverless":
        response = requests.get(COLOR_DOC)
        colour_text = response.text
    else:
        with (
            open("data/foundation/colour.md") as design_colour
        ):  # extracted from https://github.com/govtechmy/myds/tree/main/packages/style/styles/theme
            colour_text = design_colour.readlines()
    system_instruction = "You are an expert at writing React components and fixing React code with errors\nYour task is to fix the code of a React component for a web app, according to the provided detected component errors.\nAlso, the React component you write can make use of Tailwind classes for styling.\nYou will write the full React component code, which should include all imports. The fixed code you generate will be directly written to a .tsx React component file and used directly in production."

    generation_config_part2 = types.GenerateContentConfig(
        temperature=0.1,
        systemInstruction=system_instruction,
        responseMimeType="application/json",
        responseSchema=TsxOutput,
    )
    gen_code_response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        config=generation_config_part2,
        contents=[
            "**Color tokens**\n"
            + "".join(colour_text)
            + "\n\n"
            "**Component Errors**\n" + error_text,
            "\n\n**Current React component code which has errors :**\n\n"
            + generated_code
            + "\n\nRewrite the full code to fix and update the provided React web component"
            # + "The full code of the new React component that you write will be written directly to a .tsx file inside the React project. Make sure all necessary imports are done, and that your full code is enclosed with ```tsx ``` blocks.\n",
            # "\nAnswer with generated code only. DO NOT ADD ANY EXTRA TEXT DESCRIPTION OR COMMENTS BESIDES THE CODE. Your answer contains code only ! component code only !\n\n"
            # + "Important :\n\n"
            # + "- Make sure you import the components libraries and icons that are provided to you (if you use them) !\n"
            # + "- Tailwind classes should be written directly in the elements class tags (or className in case of React). DO NOT WRITE ANY CSS OUTSIDE OF CLASSES\n"
            # + "- DO NOT USE ANY <style> IN THE CODE ! CLASSES STYLING ONLY !\n"
            # + "- DO NOT USE LIBRARIES OR IMPORTS EXCEPT WHAT IS PROVIDED IN THIS TASK; OTHERWISE IT WOULD CRASH THE COMPONENT BECAUSE NOT INSTALLED. DO NOT IMPORT EXTRA LIBRARIES BESIDES WHAT IS PROVIDED !\n"
            # + "- Do not have ANY dynamic data! Components are meant to be working as is without supplying any variable to them when importing them ! Only write a component that render directly with placeholders as data, component not supplied with any dynamic data.\n"
            # + "- Fix all errors according to the provided errors data\n"
            # + "- You are allowed to remove any problematic part of the code and replace it\n"
            # + "- Only use the `@govtechmy/myds-react` and `@govtechmy/myds-style` libraries !\n"
            # + "- Only write the code for the component; Do not write extra code to import it! The code will directly be stored in an individual React .tsx file\n"
            + "- Very important : Your component should be exported as default !\n"
            + "Fix and write the updated version of the React component code as the creative genius and React component genius you are.",
        ],
    )
    generated_code = json.loads(gen_code_response.text)

    with open(file_name, "w+") as f:
        f.write(generated_code["tsx"].replace("```tsx\n", "").replace("\n```", ""))
    if os.getenv("WEB_LOCAL_MODULE_PATH") and file_name != os.getenv(
        "WEB_LOCAL_MODULE_PATH"
    ):
        with open(os.getenv("WEB_LOCAL_MODULE_PATH"), "w+") as f:
            f.write(generated_code["tsx"].replace("```tsx\n", "").replace("\n```", ""))

    return generated_code["tsx"]


def validate_full(generated_code, component_name="test"):
    if os.getenv("DEP_TYPE") == "serverless":
        file_name = "/tmp/test.tsx"
        with open(file_name, "w+") as f:
            f.write(generated_code.replace("```tsx\n", "").replace("\n```", ""))
    else:
        file_name = f"output/{component_name}.tsx"

        if not os.path.isfile(file_name):
            if os.getenv("WEB_LOCAL_MODULE_PATH"):
                file_name = os.getenv("WEB_LOCAL_MODULE_PATH")
            with open(file_name, "w+") as f:
                f.write(generated_code.replace("```tsx\n", "").replace("\n```", ""))
    # lint_error = validate_lint(file_name)
    lint_error = []
    compile_error = validate_tsc(file_name)

    error_text = "\n".join(
        [f"{i + 1}. {x}" for i, x in enumerate(lint_error + compile_error)]
    )

    fixed_code = fix_code_gemini(error_text, generated_code, file_name)

    lint_error = validate_lint(file_name)
    compile_error = validate_tsc(file_name)
    total_error = lint_error + compile_error
    fix_turn = 1
    num_tries = 5
    while total_error and fix_turn <= num_tries:
        # print(f"validation try: {fix_turn}/5")
        fix_turn += 1
        error_text = "\n".join([f"{i + 1}. {x}" for i, x in enumerate(total_error)])

        fixed_code = fix_code_gemini(error_text, generated_code, file_name)

        lint_error = validate_lint(file_name)
        compile_error = validate_tsc(file_name)
        total_error = lint_error + compile_error

    return fixed_code
