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
from memory import load_memory, save_memory
from prompts import SYSTEM_PROMPT

dotenv_path = ".env"
if not os.path.exists(dotenv_path):
    alt_path = "env"
    if os.path.exists(alt_path):
        dotenv_path = alt_path

load_dotenv(dotenv_path=dotenv_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print("DEBUG KEY =", OPENROUTER_API_KEY)
print("Loaded env file:", dotenv_path)

MODEL          = "nvidia/nemotron-3-super-120b-a12b:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def get_openrouter_api_key():
    if OPENROUTER_API_KEY:
        return OPENROUTER_API_KEY
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set. Create a .env file with "
        "OPENROUTER_API_KEY=your_key or set the environment variable."
    )


# ─────────────────────────────────────────
# Tool schemas shown to the LLM
# ─────────────────────────────────────────
TOOLS = [

    # ── Calculator ───────────────────────
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

    # ── BMI ──────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "bmi_calculator",
            "description": (
                "Calculate BMI and classify it (Underweight / Normal / Overweight / Obese). "
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

    # ── Age ──────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "age_calculator",
            "description": (
                "Calculate exact age from date of birth. "
                "Use when the user provides a birth date or asks how old someone is."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "birth_year":  {"type": "integer", "description": "Year of birth e.g. 2004"},
                    "birth_month": {"type": "integer", "description": "Month of birth 1–12"},
                    "birth_day":   {"type": "integer", "description": "Day of birth 1–31"}
                },
                "required": ["birth_year", "birth_month", "birth_day"]
            }
        }
    },

    # ── Grade ─────────────────────────────
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

    # ── Weather by city ───────────────────
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Get current live weather for any city by name. "
                "Use when user asks about weather, temperature, or conditions in a city."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name e.g. Chennai, London, New York"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "metric = Celsius, imperial = Fahrenheit. Default: metric"
                    }
                },
                "required": ["city"]
            }
        }
    },

    # ── Weather by coordinates ────────────
    {
        "type": "function",
        "function": {
            "name": "get_weather_by_coordinates",
            "description": (
                "Get current weather using latitude and longitude. "
                "Use when the user provides lat/lon coordinates."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "lat":   {"type": "number", "description": "Latitude e.g. 13.0827"},
                    "lon":   {"type": "number", "description": "Longitude e.g. 80.2707"},
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "metric = Celsius, imperial = Fahrenheit. Default: metric"
                    }
                },
                "required": ["lat", "lon"]
            }
        }
    },

    # ── Currency convert ──────────────────
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": (
                "Convert an amount from one currency to another using live rates. "
                "Use when user says 'convert 500 INR to USD' or 'how much is X in Y'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount":        {"type": "number", "description": "Amount to convert e.g. 500"},
                    "from_currency": {"type": "string", "description": "Source currency code e.g. INR"},
                    "to_currency":   {"type": "string", "description": "Target currency code e.g. USD"}
                },
                "required": ["amount", "from_currency", "to_currency"]
            }
        }
    },

    # ── Currency list ─────────────────────
    {
        "type": "function",
        "function": {
            "name": "list_currencies",
            "description": (
                "List all supported currency codes and names. "
                "Use when user asks what currencies are available."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # ── Currency compare ──────────────────
    {
        "type": "function",
        "function": {
            "name": "compare_currency",
            "description": (
                "Compare one base currency against multiple currencies at once. "
                "Use when user says 'compare USD against INR, EUR and GBP'."
            ),
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
                        "description": "Target currency codes e.g. ['INR', 'EUR', 'GBP']"
                    }
                },
                "required": ["base_currency", "target_currencies"]
            }
        }
    },

    # ── Country info ──────────────────────
    {
        "type": "function",
        "function": {
            "name": "get_country_info",
            "description": (
                "Get detailed information about a country: capital, population, "
                "languages, currency, region, timezones, calling code and flag. "
                "Use when the user asks 'tell me about India' or 'info on Germany'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "country_name": {
                        "type": "string",
                        "description": "Full or partial country name e.g. India, Germany, Japan"
                    }
                },
                "required": ["country_name"]
            }
        }
    },

    # ── Countries by region ───────────────
    {
        "type": "function",
        "function": {
            "name": "search_countries_by_region",
            "description": (
                "List all countries in a world region. "
                "Use when user asks 'list countries in Asia' or 'countries in Europe'. "
                "Valid regions: Africa, Americas, Asia, Europe, Oceania, Antarctic."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name: Africa, Americas, Asia, Europe, Oceania, Antarctic"
                    }
                },
                "required": ["region"]
            }
        }
    },

    # ── Books by title ────────────────────
    {
        "type": "function",
        "function": {
            "name": "search_books_by_title",
            "description": (
                "Search for books by title using Open Library. "
                "Use when user says 'search books named Atomic Habits' "
                "or 'find a book called Wings of Fire'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Book title to search e.g. Atomic Habits"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return (1–10). Default 5."
                    }
                },
                "required": ["title"]
            }
        }
    },

    # ── Books by author ───────────────────
    {
        "type": "function",
        "function": {
            "name": "search_books_by_author",
            "description": (
                "Search for books written by a specific author. "
                "Use when user says 'books by APJ Abdul Kalam' or "
                "'show me books written by Chetan Bhagat'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "author": {
                        "type": "string",
                        "description": "Author name e.g. APJ Abdul Kalam"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return (1–10). Default 5."
                    }
                },
                "required": ["author"]
            }
        }
    },

    # ── Book by ISBN ──────────────────────
    {
        "type": "function",
        "function": {
            "name": "get_book_by_isbn",
            "description": (
                "Get detailed info about a specific book using its ISBN number. "
                "Use when user provides an ISBN like '9780735224292' or "
                "asks to 'look up book with ISBN'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "isbn": {
                        "type": "string",
                        "description": "ISBN-10 or ISBN-13 number e.g. 9780735224292"
                    }
                },
                "required": ["isbn"]
            }
        }
    }
]

# ─────────────────────────────────────────
# Map tool name → Python function
# ─────────────────────────────────────────
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


def call_llm(messages):
    headers = {
        "Authorization": f"Bearer {get_openrouter_api_key()}",
        "Content-Type": "application/json"
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
        result = TOOL_FUNCTIONS[tool_name](**tool_args)
        return str(result)
    else:
        return f"Error: Tool '{tool_name}' not found."


def agent_loop(user_input):
    memory   = load_memory()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(memory)
    messages.append({"role": "user", "content": user_input})

    max_steps = 5

    for step in range(max_steps):
        result  = call_llm(messages)
        message = result["choices"][0]["message"]
        messages.append(message)

        if "tool_calls" in message and message["tool_calls"]:
            for tool_call in message["tool_calls"]:
                tool_result = run_tool(tool_call)

                print(f"\n  [Tool]   {tool_call['function']['name']}")
                print(f"  [Result] {tool_result}\n")

                messages.append({
                    "role":        "tool",
                    "tool_call_id": tool_call["id"],
                    "name":         tool_call["function"]["name"],
                    "content":      tool_result
                })
        else:
            final_answer = message.get("content", "No response generated.")
            save_memory(messages[1:])
            return final_answer

    return "Stopped: maximum tool loop steps reached."


if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY is not set.")
        raise SystemExit(1)

    print("Agent ready.")
    print("Type 'exit' to stop.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        try:
            answer = agent_loop(user_input)
            print("Agent:", answer)
        except Exception as e:
            print("Error:", e)