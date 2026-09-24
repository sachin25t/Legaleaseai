# LegalEase

LegalEase is an AI-assisted legal document drafting prototype with a FastAPI backend and Streamlit frontend.

## Setup

Open the `LegalEase` folder in VS Code, then run these commands in Terminal 1:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and provide your Gemini API key:

```dotenv
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.8-flash
DEMO_MODE=false
BACKEND_URL=http://127.0.0.1:8000
```

Keep `.env` private. The `GEMINI_API_KEY` value is loaded from the environment by the backend.

## Run the backend

In Terminal 1, with the virtual environment activated:

```powershell
uvicorn backend.main:app --reload --port 8000
```

Open the API at [http://127.0.0.1:8000](http://127.0.0.1:8000). Interactive API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Run the frontend

Open Terminal 2:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

Open the Streamlit URL shown in the terminal, normally [http://localhost:8501](http://localhost:8501).

## Demo mode

Set this value in `.env` before restarting the backend:

```dotenv
DEMO_MODE=true
```

The current application code does not yet read `DEMO_MODE`; enabling this variable alone does not switch generation to a demo provider. Gemini generation therefore still requires the configured API key unless demo-mode support is added to the backend.