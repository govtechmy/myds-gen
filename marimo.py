import marimo

__generated_with = "0.11.9"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.callout("Only generation is available at the current stage", kind="warn")
    return


@app.cell
def _():
    import os
    import marimo as mo
    from util.stages import design, component_generation, build_context

    return build_context, component_generation, design, mo, os


@app.cell
def _(mo):
    prompt_ui = mo.ui.text_area(
        label="Describe your desired component",
        placeholder="eg: a pricing component for a SaaS, a gallery for article previews",
        full_width=True,
    )
    prompt_ui
    return (prompt_ui,)


@app.cell
def _(mo):
    button = mo.ui.run_button(label="Click to generate component")
    button
    return (button,)


@app.cell
def _(build_context, button, component_generation, design, mo, prompt_ui):
    prompt = prompt_ui.text
    mo.stop(not button.value)
    with mo.status.spinner(subtitle="Learning about the prompt...") as _spinner:
        valid_prompt = design.prompt_validation(prompt)
    
        if valid_prompt:
            design_data = design.design_planning(prompt)
            _spinner.update(subtitle="Gathering knowledge...")
            component_task, full_context = build_context.generate(prompt, design_data)
            _spinner.update(subtitle="Generating component...")
            component_string = component_generation.generate(component_task,full_context)
            tsx_download = mo.download(
                data=component_string.replace("```tsx\n", "").replace(
                    "\n```", ""
                ),
                filename=f"{component_task['name']}.tsx",
                mimetype="text/plain",
            )
        else:
            prompt_invalid = mo.callout(
                "Please enter a valid component prompt", kind="danger"
            )
    return (
        component_string,
        component_task,
        design_data,
        full_context,
        prompt,
        prompt_invalid,
        tsx_download,
        valid_prompt,
    )


@app.cell
def _(component_string, mo):
    mo.vstack(
        [
            mo.md("# Code Generated"),
            mo.callout(mo.md(component_string), kind="info"),
        ]
    )
    return


@app.cell
def _(tsx_download):
    tsx_download
    return


@app.cell
def _(prompt_invalid):
    prompt_invalid
    return


if __name__ == "__main__":
    app.run()
