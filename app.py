import streamlit as st
import os
import json
import requests
from dotenv import load_dotenv

from tools import (
    calculator,
    bmi_calculator,
    age_calculator,
    grade_calculator,
    get_weather,
    get_weather_by_coordinates,
    convert_currency,
    list_currencies,
    compare_currency,
    get_country_info,
    search_countries_by_region,
    search_books_by_title,
    search_books_by_author,
    get_book_by_isbn,
)
from prompts import SYSTEM_PROMPT

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL              = "nvidia/nemotron-3-super-120b-a12b:free"
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"

# ─────────────────────────────────────────
# Tool registry
# ─────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform basic arithmetic: add, subtract, multiply, or divide two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                    "operation": {
                        "type": "string",
                        "enum": ["add", "sub", "mul", "div"],
                        "description": "Arithmetic operation"
                    }
                },
                "required": ["a", "b", "operation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bmi_calculator",
            "description": (
                "Calculate BMI and classify it. "
                "Use when the user provides weight and height."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "weight_kg": {"type": "number", "description": "Weight in kilograms"},
                    "height_cm": {"type": "number", "description": "Height in centimeters"}
                },
                "required": ["weight_kg", "height_cm"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "age_calculator",
            "description": (
                "Calculate exact age from date of birth. "
                "Use when the user provides a birth date."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "birth_year":  {"type": "integer", "description": "Year of birth"},
                    "birth_month": {"type": "integer", "description": "Month of birth 1-12"},
                    "birth_day":   {"type": "integer", "description": "Day of birth 1-31"}
                },
                "required": ["birth_year", "birth_month", "birth_day"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grade_calculator",
            "description": (
                "Calculate average percentage and letter grade from subject scores. "
                "Use when the user provides marks or scores."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "scores": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of scores e.g. [85, 90, 78]"
                    },
                    "max_score": {
                        "type": "number",
                        "description": "Max score per subject. Defaults to 100."
                    }
                },
                "required": ["scores"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Get current live weather for any city by name. "
                "Use when user asks about weather in a city."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city":  {"type": "string", "description": "City name e.g. Chennai"},
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "metric=Celsius, imperial=Fahrenheit. Default: metric"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_by_coordinates",
            "description": "Get weather using latitude and longitude coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lat":   {"type": "number", "description": "Latitude"},
                    "lon":   {"type": "number", "description": "Longitude"},
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "Default: metric"
                    }
                },
                "required": ["lat", "lon"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert amount between currencies using live rates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount":        {"type": "number", "description": "Amount to convert"},
                    "from_currency": {"type": "string", "description": "Source currency code e.g. INR"},
                    "to_currency":   {"type": "string", "description": "Target currency code e.g. USD"}
                },
                "required": ["amount", "from_currency", "to_currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_currencies",
            "description": "List all supported currency codes and names.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_currency",
            "description": "Compare one base currency against multiple currencies at once.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_currency": {
                        "type": "string",
                        "description": "Base currency code e.g. USD"
                    },
                    "target_currencies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of target codes e.g. ['INR','EUR','GBP']"
                    }
                },
                "required": ["base_currency", "target_currencies"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_country_info",
            "description": "Get detailed info about a country by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country_name": {
                        "type": "string",
                        "description": "Country name e.g. India, Germany"
                    }
                },
                "required": ["country_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_countries_by_region",
            "description": "List all countries in a world region.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Africa, Americas, Asia, Europe, Oceania, Antarctic"
                    }
                },
                "required": ["region"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_books_by_title",
            "description": "Search for books by title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Book title to search"},
                    "limit": {"type": "integer", "description": "Number of results (1-10)"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_books_by_author",
            "description": "Search for books written by a specific author.",
            "parameters": {
                "type": "object",
                "properties": {
                    "author": {"type": "string", "description": "Author name"},
                    "limit":  {"type": "integer", "description": "Number of results (1-10)"}
                },
                "required": ["author"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_book_by_isbn",
            "description": "Get book details using ISBN number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "isbn": {"type": "string", "description": "ISBN-10 or ISBN-13"}
                },
                "required": ["isbn"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "calculator":                 calculator,
    "bmi_calculator":             bmi_calculator,
    "age_calculator":             age_calculator,
    "grade_calculator":           grade_calculator,
    "get_weather":                get_weather,
    "get_weather_by_coordinates": get_weather_by_coordinates,
    "convert_currency":           convert_currency,
    "list_currencies":            list_currencies,
    "compare_currency":           compare_currency,
    "get_country_info":           get_country_info,
    "search_countries_by_region": search_countries_by_region,
    "search_books_by_title":      search_books_by_title,
    "search_books_by_author":     search_books_by_author,
    "get_book_by_isbn":           get_book_by_isbn,
}


# ─────────────────────────────────────────
# Core agent functions
# ─────────────────────────────────────────

def call_llm(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type":  "application/json"
    }
    payload = {
        "model":    MODEL,
        "messages": messages,
        "tools":    TOOLS
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def run_tool(tool_call):
    tool_name = tool_call["function"]["name"]
    tool_args = json.loads(tool_call["function"]["arguments"])
    if tool_name in TOOL_FUNCTIONS:
        return str(TOOL_FUNCTIONS[tool_name](**tool_args))
    return f"Error: Tool '{tool_name}' not found."


def agent_loop(user_input, chat_history):
    """
    Runs the agent loop.
    chat_history -> list of {role, content} dicts from Streamlit session
    Returns (final_answer, tools_used)
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Convert streamlit history to LLM message format
    for msg in chat_history:
        messages.append({
            "role":    msg["role"],
            "content": msg["content"]
        })

    messages.append({"role": "user", "content": user_input})

    tools_used = []
    max_steps  = 5

    for step in range(max_steps):
        result  = call_llm(messages)
        message = result["choices"][0]["message"]
        messages.append(message)

        if "tool_calls" in message and message["tool_calls"]:
            for tool_call in message["tool_calls"]:
                tool_name   = tool_call["function"]["name"]
                tool_result = run_tool(tool_call)

                tools_used.append({
                    "tool":   tool_name,
                    "result": tool_result
                })

                messages.append({
                    "role":        "tool",
                    "tool_call_id": tool_call["id"],
                    "name":         tool_name,
                    "content":      tool_result
                })
        else:
            final_answer = message.get("content", "No response generated.")
            return final_answer, tools_used

    return "Stopped: maximum steps reached.", tools_used


# ─────────────────────────────────────────
# Streamlit UI
# ─────────────────────────────────────────

# Page config
st.set_page_config(
    page_title = "Multi-Tool AI Agent",
    page_icon  = "🤖",
    layout     = "wide"
)

# Custom CSS
st.markdown("""
    <style>
        .stChatMessage { padding: 0.5rem 1rem; }
        .tool-badge {
            background-color: #1e3a5f;
            color: #7dd3fc;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-family: monospace;
            display: inline-block;
            margin: 2px 2px;
        }
        .tool-box {
            background-color: #0f172a;
            border-left: 3px solid #3b82f6;
            border-radius: 6px;
            padding: 0.6rem 1rem;
            margin-top: 0.4rem;
            font-size: 0.82rem;
            color: #94a3b8;
            font-family: monospace;
            white-space: pre-wrap;
        }
    </style>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────
with st.sidebar:
    st.title("🤖 Multi-Tool AI Agent")
    st.markdown("---")

    st.markdown("### 🛠️ Available Tools")

    tools_info = {
        "➕ Math":               ["calculator"],
        "🏥 Health":             ["bmi_calculator", "age_calculator"],
        "🎓 Academics":          ["grade_calculator"],
        "🌤️ Weather":            ["get_weather", "get_weather_by_coordinates"],
        "💱 Currency":           ["convert_currency", "list_currencies", "compare_currency"],
        "🌍 Country Info":       ["get_country_info", "search_countries_by_region"],
        "📚 Book Search":        ["search_books_by_title", "search_books_by_author", "get_book_by_isbn"],
    }

    for domain, tools in tools_info.items():
        with st.expander(domain):
            for t in tools:
                st.markdown(f"`{t}`")

    st.markdown("---")

    st.markdown("### 💡 Try These")
    examples = [
        "What is 1847293 × 6492?",
        "My weight is 68kg height 172cm",
        "I was born on 5 June 2004",
        "My scores are 88, 76, 91, 84",
        "Weather in Chennai",
        "Convert 500 INR to USD",
        "Compare USD vs INR, EUR, GBP",
        "Tell me about Japan",
        "List countries in Asia",
        "Books by APJ Abdul Kalam",
        "Search books named Atomic Habits",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state["prefill"] = example

    st.markdown("---")

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

    st.markdown("---")
    st.caption("Built with OpenRouter · Nemotron 120B · ReAct Pattern")


# ── Main area ────────────────────────────
st.title("🤖 Multi-Tool AI Agent")
st.caption(
    "Ask me anything — weather, currency, country info, books, "
    "BMI, age, grades, or math."
)

# Check API key
if not OPENROUTER_API_KEY:
    st.error(
        "⚠️ OPENROUTER_API_KEY is not set. "
        "Add it to your .env file and restart."
    )
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Render existing chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Show tool usage under assistant messages
        if msg["role"] == "assistant" and msg.get("tools_used"):
            with st.expander("🔧 Tools used", expanded=False):
                for t in msg["tools_used"]:
                    st.markdown(
                        f'<span class="tool-badge">⚙️ {t["tool"]}</span>',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f'<div class="tool-box">{t["result"]}</div>',
                        unsafe_allow_html=True
                    )

# Handle sidebar example button prefill
prefill_text = st.session_state.pop("prefill", None)

# Chat input
user_input = st.chat_input("Ask me anything...") or prefill_text

if user_input:
    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Add to session history
    st.session_state["messages"].append({
        "role":    "user",
        "content": user_input
    })

    # Run agent and show response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer, tools_used = agent_loop(
                    user_input,
                    st.session_state["messages"][:-1]  # exclude current user msg
                )

                st.markdown(answer)

                # Show tools used if any
                if tools_used:
                    with st.expander("🔧 Tools used", expanded=False):
                        for t in tools_used:
                            st.markdown(
                                f'<span class="tool-badge">⚙️ {t["tool"]}</span>',
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f'<div class="tool-box">{t["result"]}</div>',
                                unsafe_allow_html=True
                            )

            except Exception as e:
                answer     = f"❌ Error: {str(e)}"
                tools_used = []
                st.error(answer)

    # Save assistant response to session history
    st.session_state["messages"].append({
        "role":       "assistant",
        "content":    answer,
        "tools_used": tools_used
    })