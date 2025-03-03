# Setting up the env
1. install packages using [uv](https://github.com/astral-sh/uv)
```sh
uv sync
```

2. create `.env` and add your Gemini API key as in `.env.example`

3. install eslint
```sh
npm i eslint --save-dev
```
4. install tsc
```sh
npm install typescript --save-dev
```

# Setting up data:
1. simple myds db
```sh
uv run data/components/extract.py
```

2. icons vector db
```sh
uv run data/icons/build_icon_vector.py
```

# Running in cli:
```sh
uv run main.py
```

# Running marimo app
```sh
uv run marimo run marimo.py
```

# Workflow
![workflow](process.png)