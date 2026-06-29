# Agentic AI

A simple beginner-friendly Python chat agent that uses OpenRouter.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file from the example:

   ```bash
   copy .env.example .env
   ```

3. Add your OpenRouter API key to `.env`:

   ```ini
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

4. Run the agent:

   ```bash
   python main.py
   ```

## Notes

- If you see `DEBUG KEY = None`, the API key was not loaded.
- Make sure `.env` is in the same folder as `main.py`.
- If you prefer, you can also set the environment variable directly:

  ```powershell
  $env:OPENROUTER_API_KEY = "your_openrouter_api_key_here"
  python main.py
  ```
