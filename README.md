# Setting up the env
1. install packages using [uv](https://github.com/astral-sh/uv)
```bash
uv sync
```

2. create `.env` and add your Gemini API key as in `.env.example`

# Setting up data:
1. simple myds db
```bash
uv run data/components/extract.py
```

2. icons vector db
```bash
uv run data/icons/build_icon_vector.py
```

# Running in cli:
```bash
uv run main.py
```