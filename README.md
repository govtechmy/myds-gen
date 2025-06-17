# [WIP] MYDS-Gen
A MYDS component generator

## Setting up the env
1. install packages using [uv](https://github.com/astral-sh/uv)
```sh
uv sync
```

2. install js modules
```sh
npm i
```

## Setting up data:
1. myds component db
```sh
uv run data/components/extract.py
```

2. icons vector db
```sh
uv run data/icons/build_icon_vector.py
```

## Running locally:
```sh
npm run dev-local
```
Access the page on http://localhost:3000/

## Workflow
```mermaid
%%{ init: { 'flowchart': { 'curve': '1' } } }%%
flowchart LR
    subgraph init
        direction LR
        subgraph design_plan[Design and Planning]
            prompt_validation[Prompt Validation]
            valid_check_sub@{shape: diamond, label: "Prompt is valid"}
            subgraph learner
                direction TB
                prompt_enhancement[Enhance user prompt to be more descriptive & detailed]
                component_rag[Retrieve relevant MYDS components using RAG]
                design_planning[Generate a task outline]
                wireframe_gen[Generate wireframe of component]
                build_context[Compiled context]

                prompt_enhancement-->component_rag-->design_planning-->wireframe_gen-->build_context
            end

            prompt_validation --> valid_check_sub
            valid_check_sub -- Yes --> learner
            valid_check_sub -- No --> invalid[Invalid Prompt]
        end

        subgraph generate_component[Component Generation]
            direction LR
            generate[Generate Component with compiled context]
            subgraph init_outputs
            direction TB
                output[Component code]
                history[Context history]
            end
    
            generate --> init_outputs
        end

        user_prompt@{ shape: lean-r, label: "User Prompt" }
        valid_check@{shape: diamond, label: "Prompt is valid"}
        output_init[Output]

        user_prompt --> design_plan
        design_plan --> valid_check
        valid_check -- Yes --> generate
        valid_check -- No --> err[Prompt Invalid]
        generate_component --> output_init
        err --> output_init
    end

    subgraph iter[Itertion]
        direction LR
        subgraph design_plan_iter[Update design & generate]
            direction TB
            prompt_enhancement_iter[Enhance User Prompt]
            design_update[Update component design context based on context history and user prompt]
            generate_component_iter[Generate component based on updated design context]
            subgraph iter_outputs[Output for iteration]
                direction TB
                    output_iter[Updated component code]
                    history_iter[Updated context history]
            end
            prompt_enhancement_iter --> design_update --> generate_component_iter --> iter_outputs
        end

        user_prompt_iter@{ shape: lean-r, label: "User prompt for iteration" }
        output_general[ Historical Design Context]
        join_data@{shape: fork, label: "Join data"}
        output_f_iter[Output]
        user_prompt_iter --> join_data --> design_plan_iter --> output_f_iter
        %% output_f_iter --> output_general
    end
    
    
    output_init --> output_general
    output_general --> join_data

    style init fill:#FFFFFF00
    style iter fill:#FFFFFF00
```
