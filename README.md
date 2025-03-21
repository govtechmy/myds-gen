# Setting up the env
1. install packages using [uv](https://github.com/astral-sh/uv)
```sh
uv sync
```

2. create `.env` and add your Gemini API key as in `.env.example`

3. install js modules
```sh
npm i
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

# Running locally:
```sh
npm run dev-local
```

Access the page on http://localhost:3000/

# Running locally with streamlit:
```sh
npm run dev-local-streamlit
```
**The streamlit preview will be available on http://localhost:8501**

# Examples
1. Python module usage - [example.ipynb](examples/example.ipynb)
2. API usage - [example-api.ipynb](examples/example-api.ipynb)

# Workflow
![workflow](process.png)