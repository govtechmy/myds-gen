import json
import os
import re
import subprocess
from time import sleep
from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)


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


def validate_lint(file_name):
    result = subprocess.run(
        ["npx", "eslint", "--fix", file_name, "--format", "json"],
        capture_output=True,
        text=True,  # Decode bytes to string
        check=False,
    )
    errors = [
        f"{i['ruleId']}: {i['message']}"
        for i in json.loads(result.stdout)[0]["messages"]
    ]
    return errors


def validate_tsc(file_name):
    result = subprocess.run(
        [
            "tsc",
            file_name,
            "--jsx",
            "react-jsx",
            "--noEmit",
            "--moduleResolution",
            "node16",
            "--module",
            "node16",
        ],
        capture_output=True,
        text=True,  # Decode bytes to string
        check=False,
    )
    errors = list(set([i.strip() for i in re.findall(r":([\s\S]+?)\n", result.stdout)]))
    return errors


def fix_code_gemini(error_text, generated_code, component_name):
    system_instruction = "You are an expert at writing React components and fixing React code with errors\nYour task is to fix the code of a React component for a web app, according to the provided detected component errors.\nAlso, the React component you write can make use of Tailwind classes for styling.\nYou will write the full React component code, which should include all imports. The fixed code you generate will be directly written to a .tsx React component file and used directly in production."

    generation_config_part2 = types.GenerateContentConfig(
        temperature=0.4,
        systemInstruction=system_instruction,
    )
    gen_code_response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=generation_config_part2,
        contents=[
            "**Component Errors**\n" + error_text,
            "\n\n**Current React component code which has errors :**\n\n"
            + generated_code
            + "\n\nRewrite the full code to fix and update the provided React web component"
            + "The full code of the new React component that you write will be written directly to a .tsx file inside the React project. Make sure all necessary imports are done, and that your full code is enclosed with ```tsx ``` blocks.\n",
            "\nAnswer with generated code only. DO NOT ADD ANY EXTRA TEXT DESCRIPTION OR COMMENTS BESIDES THE CODE. Your answer contains code only ! component code only !\n\n"
            + "Important :\n\n"
            + "- Make sure you import the components libraries and icons that are provided to you (if you use them) !\n"
            + "- Tailwind classes should be written directly in the elements class tags (or className in case of React). DO NOT WRITE ANY CSS OUTSIDE OF CLASSES\n"
            + "- Do not use libraries or imports except what is provided in this task; otherwise it would crash the component because not installed. Do not import extra libraries besides what is provided !\n"
            + "- Do not have ANY dynamic data! Components are meant to be working as is without supplying any variable to them when importing them ! Only write a component that render directly with placeholders as data, component not supplied with any dynamic data.\n"
            + "- Fix all errors according to the provided errors data\n"
            + "- You are allowed to remove any problematic part of the code and replace it\n"
            + "- Only use the `@govtechmy/myds-react` and `@govtechmy/myds-style` libraries !\n"
            + "- Only write the code for the component; Do not write extra code to import it! The code will directly be stored in an individual React .tsx file\n"
            + "- Very important : Your component should be exported as default !\n"
            + "Fix and write the updated version of the React component code as the creative genius and React component genius you are.",
        ],
    )

    with open(f"output/{component_name}.tsx", "w+") as f:
        f.write(gen_code_response.text.replace("```tsx\n", "").replace("\n```", ""))

    # sleep(10)
    return gen_code_response.text


def validate_full(generated_code, component_name):
    file_name = f"output/{component_name}.tsx"
    lint_error = validate_lint(file_name)
    compile_error = validate_tsc(file_name)

    error_text = "\n".join(
        [f"{i + 1}. {x}" for i, x in enumerate(lint_error + compile_error)]
    )

    fixed_code = fix_code_gemini(error_text, generated_code, component_name)

    lint_error = validate_lint(file_name)
    compile_error = validate_tsc(file_name)
    total_error = lint_error + compile_error
    fix_turn = 1
    num_tries = 5
    while total_error and fix_turn < num_tries:
        print(f"validation try: {fix_turn}/5")
        fix_turn += 1
        error_text = "\n".join([f"{i + 1}. {x}" for i, x in enumerate(total_error)])

        fixed_code = fix_code_gemini(error_text, generated_code, component_name)

        lint_error = validate_lint(file_name)
        compile_error = validate_tsc(file_name)

    return fixed_code
