import os
import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
import requests as re
from src.stages.generation_validation import validate_full

API_ENDPOINT = "http://localhost:3000/"
MYDS_GEN_API = os.getenv("MYDS_GEN_API")
WEB_LOCAL_MODULE_PATH = os.getenv("WEB_LOCAL_MODULE_PATH")
headers = {"X-API-KEY": MYDS_GEN_API}

st.set_page_config(page_title="jEN Demo", layout="wide")
st.title("jEN Demo")

page_height = streamlit_js_eval(js_expressions="screen.height", key="SCR")
container_height = page_height - 300

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.columns([3, 7])
# React to user input
with col1:
    with st.container(height=container_height, border=True):
        output = st.container(height=container_height - 100, border=False)
        # Display chat messages from history on app rerun
        with output:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    if message["role"] == "assistant":
                        st.code(
                            message["content"]
                            .replace("```tsx\n", "")
                            .replace("\n```", ""),
                            language="tsx",
                            height=400,
                            # wrap_lines=True,
                        )
                    else:
                        st.markdown(message["content"])
        with st.container():
            prompt = st.chat_input("Enter message...")
        if prompt:
            with output:
                # Display user message in chat message container
                st.chat_message("user").markdown(prompt)
                if not st.session_state.messages:
                    if re.post(
                        f"{API_ENDPOINT}/api/py/validate-new-prompt?prompt={prompt}",
                        headers=headers,
                    ).json()["valid"]:
                        gen_msg = st.chat_message("assistant")
                        gen_msg.write("On it!")
                        with st.status(
                            "Generating component...", expanded=True
                        ) as status:
                            st.write("Learning about the prompt...")
                            task_response = re.post(
                                f"{API_ENDPOINT}/api/py/task_planning?prompt={prompt}",
                                headers=headers,
                            )
                            taskObject = task_response.json()
                            st.write("Gathering knowledge...")
                            wireframe_response = re.post(
                                f"{API_ENDPOINT}/api/py/wireframe_gen",
                                json=taskObject,
                                headers=headers,
                            )
                            wireframe = wireframe_response.json()
                            st.write("Designing component ...")
                            taskObjectWithWireframe = {
                                "task": taskObject,
                                "wireframe": wireframe,
                            }
                            # print(taskObjectWithWireframe)
                            context_response = re.post(
                                f"{API_ENDPOINT}/api/py/assemble_context",
                                json=taskObjectWithWireframe,
                                headers=headers,
                            )
                            generationContext = context_response.json()
                            st.write("Generating code...")
                            taskObjectWithContext = {
                                "task": taskObject,
                                "context": generationContext,
                            }
                            generation_response = re.post(
                                f"{API_ENDPOINT}/api/py/generate_component",
                                json=taskObjectWithContext,
                                headers=headers,
                            )
                            generatedCode = generation_response.json()
                            st.write("Squashing bugs..")
                            # fixed_code_response = re.post(F"{API_ENDPOINT}/api/py/generate_component", json={"tsx":generatedCode},headers=headers)
                            # generatedCode = fixed_code_response.json()
                            # print(generatedCode)
                            generatedCode = validate_full(generated_code=generatedCode)

                            data = {
                                "task": taskObject,
                                "wireframe": wireframe,
                                "tsx": generatedCode.replace('"', '\\"'),
                            }
                            status.update(
                                label="Component Generated!",
                                state="complete",
                                expanded=True,
                            )
                            with open(WEB_LOCAL_MODULE_PATH, "w+") as f:
                                f.write(
                                    generatedCode.replace("```tsx\n", "").replace(
                                        "\n```", ""
                                    )
                                )
                        # Add user message to chat history
                        st.session_state.messages.append(
                            {"role": "user", "content": prompt, "data": data}
                        )

                        # Display assistant response in chat message container
                        with st.chat_message("assistant"):
                            st.code(
                                generatedCode.replace("```tsx\n", "").replace(
                                    "\n```", ""
                                ),
                                language="tsx",
                                height=400,
                                # wrap_lines=True,
                            )
                        # Add assistant response to chat history
                        st.session_state.messages.append(
                            {"role": "assistant", "content": generatedCode}
                        )
                    else:
                        with st.chat_message("system"):
                            st.error("Invalid prompt.", icon="🚨")
                else:
                    data_to_update = [
                        i for i in st.session_state.messages if i["role"] == "user"
                    ][-1]["data"]
                    updatedPrompt = data_to_update
                    updatedPrompt["update_prompt"] = prompt
                    gen_msg = st.chat_message("assistant")
                    gen_msg.write("On it!")
                    with st.status("Updating component...", expanded=True) as status:
                        st.write("Learning about the update ...")
                        update_task_response = re.post(
                            f"{API_ENDPOINT}/api/py/task_planning_iter",
                            json=updatedPrompt,
                            headers=headers,
                        )
                        updatetaskObject = update_task_response.json()
                        updatedWireframe = None
                        if updatetaskObject["update"]["wireframe"]:
                            st.write("Designing an updated layout")
                            wireframe_update_body = {
                                "task": updatetaskObject,
                                "wireframe": updatedPrompt["wireframe"],
                            }
                            update_wireframe_response = re.post(
                                f"{API_ENDPOINT}/api/py/wireframe_iter",
                                json=wireframe_update_body,
                                headers=headers,
                            )
                            updatedWireframe = update_wireframe_response.json()
                        st.write("Gathering knowledge ...")
                        if updatedWireframe:
                            context_update_body = {
                                "task": updatetaskObject,
                                "wireframe": updatedWireframe,
                            }
                        else:
                            context_update_body = {
                                "task": updatetaskObject,
                                "wireframe": updatedPrompt["wireframe"],
                            }
                        update_context_response = re.post(
                            f"{API_ENDPOINT}/api/py/assemble_context_iter",
                            json=context_update_body,
                            headers=headers,
                        )
                        updatedContext = update_context_response.json()
                        st.write("Updating Code ...")
                        component_update_body = {
                            "task": updatetaskObject,
                            "context": updatedContext,
                            "tsx": updatedPrompt["tsx"],
                        }
                        # print(component_update_body)
                        update_component_response = re.post(
                            f"{API_ENDPOINT}/api/py/generate_component_iterate",
                            json=component_update_body,
                            headers=headers,
                        )
                        updatedComponentCode = update_component_response.json()
                        generatedCode = updatedComponentCode
                        st.write("Squashing bugs..")
                        # fixed_code_response = re.post(F"{API_ENDPOINT}/api/py/generate_component", json={"tsx":updatedComponentCode},headers=headers)
                        # generatedCode = fixed_code_response.json()
                        generatedCode = validate_full(generated_code=generatedCode)

                        data = {
                            "task": updatedPrompt["task"],
                            "wireframe": (updatedWireframe if updatedWireframe else updatedPrompt["wireframe"]).replace('"', '\\"'),
                            "tsx": generatedCode.replace('"', '\\"'),
                        }
                        status.update(
                            label="Component Generated!",
                            state="complete",
                            expanded=True,
                        )
                        with open(WEB_LOCAL_MODULE_PATH, "w+") as f:
                            f.write(
                                generatedCode.replace("```tsx\n", "").replace(
                                    "\n```", ""
                                )
                            )
                    # Add user message to chat history
                    st.session_state.messages.append(
                        {"role": "user", "content": prompt, "data": data}
                    )

                    # Display assistant response in chat message container
                    with st.chat_message("assistant"):
                        st.code(
                            generatedCode.replace("```tsx\n", "").replace("\n```", ""),
                            language="tsx",
                            height=400,
                            # wrap_lines=True,
                        )

                    st.session_state.messages.append(
                        {"role": "assistant", "content": generatedCode}
                    )


with col2:
    if st.session_state.messages:
        components.iframe(
            "http://localhost:3000/preview", height=container_height, scrolling=True
        )
