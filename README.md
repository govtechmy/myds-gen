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
1. myds component db
```sh
uv run data/components/extract.py
```

2. icons vector db
```sh
uv run data/icons/build_icon_vector.py
```

# Running in API server:
```sh
uv run fastapi dev api/index.py
```
API can be accessed http://127.0.0.1:8000/api/py/docs

# Example usage of module
1. [example.ipynb](example.ipynb)

# Workflow
![workflow](process.png)