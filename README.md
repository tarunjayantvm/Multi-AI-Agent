# 🤖 Multi-Tool AI Agent

A **production-inspired conversational AI agent** built using the **ReAct (Reasoning + Acting)** pattern. The agent understands natural language, selects the appropriate tool, executes real-time API calls, and returns accurate, structured responses while maintaining persistent conversation memory.

---

## ✨ Features

| Domain | Tools |
|--------|-------|
| Math | `calculator` |
| Health | `bmi_calculator`, `age_calculator` |
| Academics | `grade_calculator` |
| Weather | `get_weather`, `get_weather_by_coordinates` |
| Currency | `convert_currency`, `list_currencies`, `compare_currency` |
| Country Information | `get_country_info`, `search_countries_by_region` |
| Book Search | `search_books_by_title`, `search_books_by_author`, `get_book_by_isbn` |

**Total:** **14 tools across 7 domains**

---

# 🏗️ Architecture

```text
User
 │
 ▼
Agent Loop (ReAct)
 │
 ├── LLM (Nemotron 120B via OpenRouter)
 │         │
 │         └── Select Tool
 ▼
Tool Executor
 │
 ├── Python Function
 ├── External API
 └── Local Computation
 │
 ▼
Result → LLM → Natural Language Response
 │
 ▼
Conversation Memory (JSON)
```


## 🔄 Agent Workflow

```mermaid
flowchart TD

    %% =========================
    %% Nodes
    %% =========================

    A([👤 User Input])

    B["🤖 ReAct Agent Loop"]

    C["🧠 LLM Reasoning
    (Nemotron 120B)"]

    D{"🔍 Tool Required?"}

    E["⚙️ Tool Executor"]

    F["🌐 External APIs
    / Python Functions"]

    G["📊 Tool Result"]

    H["💬 Natural Language
    Response"]

    I["💾 Save Conversation
    Memory"]

    J([✅ Response to User])

    %% =========================
    %% Connections
    %% =========================

    A --> B
    B --> C
    C --> D

    D -- Yes --> E
    E --> F
    F --> G
    G --> H

    D -- No --> H

    H --> I
    I --> J

    %% =========================
    %% Colors
    %% =========================

    classDef user fill:#4CAF50,color:#fff,stroke:#2E7D32,stroke-width:3px;

    classDef agent fill:#1976D2,color:#fff,stroke:#0D47A1,stroke-width:3px;

    classDef llm fill:#9C27B0,color:#fff,stroke:#6A1B9A,stroke-width:3px;

    classDef decision fill:#FB8C00,color:#fff,stroke:#E65100,stroke-width:3px;

    classDef tool fill:#00ACC1,color:#fff,stroke:#006064,stroke-width:3px;

    classDef api fill:#8BC34A,color:#fff,stroke:#33691E,stroke-width:3px;

    classDef result fill:#26A69A,color:#fff,stroke:#004D40,stroke-width:3px;

    classDef response fill:#EC407A,color:#fff,stroke:#880E4F,stroke-width:3px;

    classDef memory fill:#5E35B1,color:#fff,stroke:#311B92,stroke-width:3px;

    class A,J user
    class B agent
    class C llm
    class D decision
    class E tool
    class F api
    class G result
    class H response
    class I memory
```



---

# 🚀 Agent Capabilities

## 🧮 Math
- Accurate arithmetic
- Large-number multiplication
- Division

Examples:
- `What is 1847293 × 6492?`
- `Divide 99 by 7`

## ❤️ Health
- BMI Calculator
- Age Calculator

Examples:
- `My weight is 70 kg and height is 175 cm`
- `I was born on 15 March 2004`

## 🎓 Academics
- Percentage
- Grade
- Remarks

## ☁️ Weather
- Current weather
- Coordinates
- Celsius/Fahrenheit

## 💱 Currency
- Live conversion
- Currency comparison
- List currencies

## 🌍 Country Information
- Capital
- Population
- Area
- Languages
- Currency
- Region
- Timezones
- Calling codes

## 📚 Book Search
- Search by title
- Search by author
- Search by ISBN

---

# 📁 Project Structure

```text
ai-agents/
│
├── main.py
├── tools.py
├── prompts.py
├── memory.py
├── memory.json
├── .env
├── requirements.txt
└── README.md
```

---

# 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.10+ |
| LLM | Nemotron 3 Super 120B |
| Framework | ReAct Agent |
| APIs | OpenRouter, OpenWeatherMap, ExchangeRate API, RestCountries, Open Library |

---


# 💬 Sample Interactions

### Weather

```text
You: What is the weather in Chennai?

Agent:
Temperature: 33°C
Humidity: 72%
Condition: Partly Cloudy
```

### Currency

```text
You:
Convert 1000 INR to USD

Agent:
1000 INR = 11.98 USD
```

### Country

```text
You:
Tell me about Germany

Agent:
Capital: Berlin
Currency: Euro
Population: 83M
```

### Book

```text
You:
Books by APJ Abdul Kalam

Agent:
• Wings of Fire
• Ignited Minds
```

---

# 🎯 Highlights

- ReAct Agent Architecture
- Multi-tool orchestration
- Tool schema design
- Persistent conversation memory
- Live API integrations
- Production-style modular codebase

---

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
