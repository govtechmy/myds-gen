def model_mapping(selected: str) -> str:
    model_dict = {
        "Gemini-2.0-flash": "gemini-2.0-flash",
        "Gemini-2.5-pro": "gemini-2.5-pro-exp-03-25",
        "Gemini-2.5-flash": "gemini-2.5-flash-preview-04-17",
        "Gemini-2.5-flash-thinking": "gemini-2.5-flash-preview-04-17-thinking"
    }

    try:
        model = model_dict[selected]
    except KeyError:
        raise ValueError("Invalid model name")

    return model