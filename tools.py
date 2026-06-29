import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY   = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL  = "https://api.openweathermap.org/data/2.5/weather"

EXCHANGERATE_API_KEY  = os.getenv("EXCHANGERATE_API_KEY")
EXCHANGERATE_BASE_URL = "https://v6.exchangerate-api.com/v6"

RESTCOUNTRIES_BASE_URL = "https://restcountries.com/v3.1"
OPENLIBRARY_BASE_URL   = "https://openlibrary.org"


# ─────────────────────────────────────────
# Calculator
# ─────────────────────────────────────────

def calculator(a, b, operation):
    if operation == "add":
        return str(a + b)
    elif operation == "sub":
        return str(a - b)
    elif operation == "mul":
        return str(a * b)
    elif operation == "div":
        if b == 0:
            return "Error: Division by zero"
        return str(a / b)
    else:
        return "Error: Unknown operation"


# ─────────────────────────────────────────
# BMI Calculator
# ─────────────────────────────────────────

def bmi_calculator(weight_kg, height_cm):
    if weight_kg <= 0 or height_cm <= 0:
        return "Error: Weight and height must be positive numbers."

    height_m   = height_cm / 100
    bmi        = weight_kg / (height_m ** 2)
    bmi_rounded = round(bmi, 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal weight"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"

    return (
        f"BMI: {bmi_rounded} | Category: {category}\n"
        f"(Weight: {weight_kg} kg, Height: {height_cm} cm)"
    )


# ─────────────────────────────────────────
# Age Calculator
# ─────────────────────────────────────────

def age_calculator(birth_year, birth_month, birth_day):
    from datetime import date

    try:
        dob = date(birth_year, birth_month, birth_day)
    except ValueError as e:
        return f"Error: Invalid date of birth — {e}"

    today = date.today()

    if dob > today:
        return "Error: Date of birth cannot be in the future."

    age_years  = today.year  - dob.year
    age_months = today.month - dob.month
    age_days   = today.day   - dob.day

    if age_days < 0:
        age_months -= 1
        from calendar import monthrange
        prev_month = today.month - 1 if today.month > 1 else 12
        prev_year  = today.year if today.month > 1 else today.year - 1
        age_days  += monthrange(prev_year, prev_month)[1]

    if age_months < 0:
        age_years  -= 1
        age_months += 12

    return (
        f"Age: {age_years} years, {age_months} months, {age_days} days\n"
        f"(Date of Birth: {dob.strftime('%d %B %Y')})"
    )


# ─────────────────────────────────────────
# Grade Calculator
# ─────────────────────────────────────────

def grade_calculator(scores: list, max_score: float = 100.0):
    if not scores:
        return "Error: No scores provided."
    if max_score <= 0:
        return "Error: max_score must be a positive number."
    if any(s < 0 or s > max_score for s in scores):
        return f"Error: All scores must be between 0 and {max_score}."

    average            = sum(scores) / len(scores)
    percentage         = (average / max_score) * 100
    percentage_rounded = round(percentage, 2)

    if percentage >= 90:
        grade, remark = "A+", "Outstanding"
    elif percentage >= 80:
        grade, remark = "A",  "Excellent"
    elif percentage >= 70:
        grade, remark = "B",  "Good"
    elif percentage >= 60:
        grade, remark = "C",  "Average"
    elif percentage >= 50:
        grade, remark = "D",  "Below Average"
    else:
        grade, remark = "F",  "Fail"

    subject_lines = "\n".join(
        f"  Subject {i+1}: {s}/{max_score}"
        for i, s in enumerate(scores)
    )

    return (
        f"Scores:\n{subject_lines}\n"
        f"Average: {round(average, 2)}/{max_score} "
        f"({percentage_rounded}%)\n"
        f"Grade: {grade} | Remark: {remark}"
    )


# ─────────────────────────────────────────
# Weather Tools
# ─────────────────────────────────────────

def get_weather(city: str, units: str = "metric"):
    if not OPENWEATHER_API_KEY:
        return "Error: OPENWEATHER_API_KEY not set in .env"

    params = {
        "q":     city,
        "appid": OPENWEATHER_API_KEY,
        "units": units
    }

    try:
        response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=10)

        if response.status_code == 404:
            return f"Error: City '{city}' not found. Check spelling."
        if response.status_code == 401:
            return "Error: Invalid OpenWeather API key."

        response.raise_for_status()
        data = response.json()

        temp        = data["main"]["temp"]
        feels_like  = data["main"]["feels_like"]
        humidity    = data["main"]["humidity"]
        description = data["weather"][0]["description"].capitalize()
        wind_speed  = data["wind"]["speed"]
        country     = data["sys"]["country"]
        city_name   = data["name"]

        unit_symbol = "°C" if units == "metric" else "°F"
        speed_unit  = "m/s" if units == "metric" else "mph"

        return (
            f"Weather in {city_name}, {country}:\n"
            f"  Condition  : {description}\n"
            f"  Temperature: {temp}{unit_symbol} (Feels like {feels_like}{unit_symbol})\n"
            f"  Humidity   : {humidity}%\n"
            f"  Wind Speed : {wind_speed} {speed_unit}"
        )

    except requests.exceptions.ConnectionError:
        return "Error: No internet connection."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Try again."
    except Exception as e:
        return f"Error: {str(e)}"


def get_weather_by_coordinates(lat: float, lon: float, units: str = "metric"):
    if not OPENWEATHER_API_KEY:
        return "Error: OPENWEATHER_API_KEY not set in .env"

    params = {
        "lat":   lat,
        "lon":   lon,
        "appid": OPENWEATHER_API_KEY,
        "units": units
    }

    try:
        response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        temp        = data["main"]["temp"]
        feels_like  = data["main"]["feels_like"]
        humidity    = data["main"]["humidity"]
        description = data["weather"][0]["description"].capitalize()
        wind_speed  = data["wind"]["speed"]
        country     = data["sys"]["country"]
        city_name   = data["name"]

        unit_symbol = "°C" if units == "metric" else "°F"
        speed_unit  = "m/s" if units == "metric" else "mph"

        return (
            f"Weather at ({lat}, {lon}) — {city_name}, {country}:\n"
            f"  Condition  : {description}\n"
            f"  Temperature: {temp}{unit_symbol} (Feels like {feels_like}{unit_symbol})\n"
            f"  Humidity   : {humidity}%\n"
            f"  Wind Speed : {wind_speed} {speed_unit}"
        )

    except requests.exceptions.ConnectionError:
        return "Error: No internet connection."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Try again."
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# Currency Tools
# ─────────────────────────────────────────

def _check_currency_api_key():
    if not EXCHANGERATE_API_KEY:
        return "Error: EXCHANGERATE_API_KEY not set in .env"
    return None


def convert_currency(amount: float, from_currency: str, to_currency: str):
    err = _check_currency_api_key()
    if err:
        return err

    from_currency = from_currency.upper().strip()
    to_currency   = to_currency.upper().strip()

    if amount <= 0:
        return "Error: Amount must be greater than zero."

    url = f"{EXCHANGERATE_BASE_URL}/{EXCHANGERATE_API_KEY}/pair/{from_currency}/{to_currency}/{amount}"

    try:
        response = requests.get(url, timeout=10)
        data     = response.json()

        if data.get("result") == "error":
            error_type = data.get("error-type", "unknown")
            if error_type == "invalid-key":
                return "Error: Invalid ExchangeRate API key."
            elif error_type == "unsupported-code":
                return "Error: Currency code not supported. Use 'list currencies' to see valid codes."
            return f"Error: {error_type}"

        rate         = data["conversion_rate"]
        converted    = data["conversion_result"]
        last_updated = data.get("time_last_update_utc", "N/A")

        return (
            f"Currency Conversion:\n"
            f"  {amount} {from_currency} = {round(converted, 4)} {to_currency}\n"
            f"  Exchange Rate : 1 {from_currency} = {rate} {to_currency}\n"
            f"  Last Updated  : {last_updated}"
        )

    except requests.exceptions.ConnectionError:
        return "Error: No internet connection."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Try again."
    except Exception as e:
        return f"Error: {str(e)}"


def list_currencies():
    err = _check_currency_api_key()
    if err:
        return err

    url = f"{EXCHANGERATE_BASE_URL}/{EXCHANGERATE_API_KEY}/codes"

    try:
        response = requests.get(url, timeout=10)
        data     = response.json()

        if data.get("result") == "error":
            return f"Error: {data.get('error-type', 'unknown error')}"

        codes = data.get("supported_codes", [])
        if not codes:
            return "Error: No currency codes returned from API."

        lines = [f"  {code} — {name}" for code, name in codes]
        return f"Supported Currencies ({len(lines)} total):\n" + "\n".join(lines)

    except requests.exceptions.ConnectionError:
        return "Error: No internet connection."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Try again."
    except Exception as e:
        return f"Error: {str(e)}"


def compare_currency(base_currency: str, target_currencies: list):
    err = _check_currency_api_key()
    if err:
        return err

    base_currency = base_currency.upper().strip()

    if not target_currencies:
        return "Error: Please provide at least one target currency to compare."

    url = f"{EXCHANGERATE_BASE_URL}/{EXCHANGERATE_API_KEY}/latest/{base_currency}"

    try:
        response = requests.get(url, timeout=10)
        data     = response.json()

        if data.get("result") == "error":
            error_type = data.get("error-type", "unknown")
            if error_type == "unsupported-code":
                return f"Error: '{base_currency}' is not a supported currency code."
            return f"Error: {error_type}"

        all_rates    = data["conversion_rates"]
        last_updated = data.get("time_last_update_utc", "N/A")

        lines     = []
        not_found = []

        for target in target_currencies:
            target = target.upper().strip()
            if target in all_rates:
                lines.append(f"  1 {base_currency} = {all_rates[target]} {target}")
            else:
                not_found.append(target)

        if not lines:
            return "Error: None of the target currencies were found."

        result = (
            f"Comparing 1 {base_currency} against:\n" +
            "\n".join(lines) +
            f"\n  Last Updated: {last_updated}"
        )

        if not_found:
            result += f"\n  Not found: {', '.join(not_found)} (invalid codes)"

        return result

    except requests.exceptions.ConnectionError:
        return "Error: No internet connection."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Try again."
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# Country Information Tools
# ─────────────────────────────────────────

def get_country_info(country_name: str):
    url = f"{RESTCOUNTRIES_BASE_URL}/name/{country_name.strip()}"

    try:
        response = requests.get(url, timeout=15)   # ← was 10, now 15

        if response.status_code == 404:
            return f"Error: Country '{country_name}' not found. Check spelling."

        response.raise_for_status()
        results = response.json()

        data = next(
            (c for c in results
             if c.get("name", {}).get("common", "").lower() == country_name.lower()),
            results[0]
        )

        common_name  = data.get("name", {}).get("common", "N/A")
        official     = data.get("name", {}).get("official", "N/A")
        capital      = ", ".join(data.get("capital", ["N/A"]))
        region       = data.get("region", "N/A")
        subregion    = data.get("subregion", "N/A")
        population   = f"{data.get('population', 0):,}"
        area         = f"{data.get('area', 0):,} km²"
        flag         = data.get("flag", "")

        lang_raw  = data.get("languages", {})
        languages = ", ".join(lang_raw.values()) if isinstance(lang_raw, dict) else "N/A"

        curr_raw   = data.get("currencies", {})
        currencies = ", ".join(
            f"{v.get('name', k)} ({v.get('symbol', '')})"
            for k, v in curr_raw.items()
        ) if isinstance(curr_raw, dict) else "N/A"

        timezones = ", ".join(data.get("timezones", ["N/A"]))

        idd          = data.get("idd", {})
        idd_root     = idd.get("root", "")
        idd_suf      = idd.get("suffixes", [""])
        calling_code = f"{idd_root}{idd_suf[0]}" if idd_root else "N/A"

        return (
            f"{flag} Country Information: {common_name}\n"
            f"  Official Name : {official}\n"
            f"  Capital       : {capital}\n"
            f"  Region        : {region} → {subregion}\n"
            f"  Population    : {population}\n"
            f"  Area          : {area}\n"
            f"  Languages     : {languages}\n"
            f"  Currencies    : {currencies}\n"
            f"  Timezones     : {timezones}\n"
            f"  Calling Code  : {calling_code}"
        )

    except requests.exceptions.ConnectionError:
        return "Error: No internet connection."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Try again in a moment."
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


def search_countries_by_region(region: str):
    valid_regions = ["africa", "americas", "asia", "europe", "oceania", "antarctic"]
    region_clean  = region.strip().lower()

    if region_clean not in valid_regions:
        return (
            f"Error: '{region}' is not a valid region.\n"
            f"Valid regions: Africa, Americas, Asia, Europe, Oceania, Antarctic"
        )

    url = f"{RESTCOUNTRIES_BASE_URL}/region/{region_clean}"

    try:
        response = requests.get(url, timeout=15)   # ← was 10, now 15

        if response.status_code == 404:
            return f"Error: No countries found for region '{region}'."

        response.raise_for_status()
        countries = response.json()

        countries.sort(key=lambda c: c.get("name", {}).get("common", ""))

        lines = [
            f"  {i+1:>3}. {c.get('name', {}).get('common', 'N/A')}"
            f" (Pop: {c.get('population', 0):,})"
            for i, c in enumerate(countries)
        ]

        return (
            f"Countries in {region.capitalize()} ({len(lines)} total):\n" +
            "\n".join(lines)
        )

    except requests.exceptions.ConnectionError:
        return "Error: No internet connection."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Try again in a moment."
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


# ─────────────────────────────────────────
# Book Search Tools
# ─────────────────────────────────────────

def _format_book(doc: dict, index: int = None) -> str:
    """Internal helper to format a single book entry cleanly."""
    title      = doc.get("title", "N/A")
    authors    = ", ".join(doc.get("author_name", ["Unknown Author"]))
    year       = doc.get("first_publish_year", "N/A")
    isbn_list  = doc.get("isbn", [])
    isbn       = isbn_list[0] if isbn_list else "N/A"
    publisher  = ", ".join(doc.get("publisher", ["N/A"])[:2])   # max 2 publishers
    languages  = ", ".join(doc.get("language", ["N/A"])[:3])
    subjects   = ", ".join(doc.get("subject", [])[:4]) or "N/A" # max 4 subjects
    editions   = doc.get("edition_count", "N/A")

    prefix = f"  [{index}] " if index is not None else "  "

    return (
        f"{prefix}Title      : {title}\n"
        f"       Author     : {authors}\n"
        f"       Year       : {year}\n"
        f"       ISBN       : {isbn}\n"
        f"       Publisher  : {publisher}\n"
        f"       Languages  : {languages}\n"
        f"       Subjects   : {subjects}\n"
        f"       Editions   : {editions}"
    )


def search_books_by_title(title: str, limit: int = 5):
    """
    Searches for books by title using Open Library.
    title -> book title to search (e.g. "Atomic Habits")
    limit -> number of results to return (default 5, max 10)
    """
    limit = max(1, min(limit, 10))   # clamp between 1 and 10

    params = {
        "title": title.strip(),
        "limit": limit,
        "fields": "title,author_name,first_publish_year,isbn,"
                  "publisher,language,subject,edition_count"
    }

    try:
        response = requests.get(
            f"{OPENLIBRARY_BASE_URL}/search.json",
            params=params,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        docs  = data.get("docs", [])
        total = data.get("numFound", 0)

        if not docs:
            return f"No books found for title '{title}'."

        header = f"Books matching '{title}' (showing {len(docs)} of {total:,} results):\n"
        entries = [_format_book(doc, i + 1) for i, doc in enumerate(docs)]

        return header + "\n\n".join(entries)

    except requests.exceptions.ConnectionError:
        return "Error: No internet connection."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Try again."
    except Exception as e:
        return f"Error: {str(e)}"


def search_books_by_author(author: str, limit: int = 5):
    """
    Searches for books written by a specific author.
    author -> author name (e.g. "APJ Abdul Kalam", "Chetan Bhagat")
    limit  -> number of results to return (default 5, max 10)
    """
    limit = max(1, min(limit, 10))

    params = {
        "author": author.strip(),
        "limit":  limit,
        "fields": "title,author_name,first_publish_year,isbn,"
                  "publisher,language,subject,edition_count"
    }

    try:
        response = requests.get(
            f"{OPENLIBRARY_BASE_URL}/search.json",
            params=params,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        docs  = data.get("docs", [])
        total = data.get("numFound", 0)

        if not docs:
            return f"No books found for author '{author}'."

        header  = f"Books by '{author}' (showing {len(docs)} of {total:,} results):\n"
        entries = [_format_book(doc, i + 1) for i, doc in enumerate(docs)]

        return header + "\n\n".join(entries)

    except requests.exceptions.ConnectionError:
        return "Error: No internet connection."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Try again."
    except Exception as e:
        return f"Error: {str(e)}"


def get_book_by_isbn(isbn: str):
    """
    Fetches detailed info about a specific book using its ISBN.
    isbn -> 10 or 13 digit ISBN number (e.g. "9780735224292")
    """
    isbn_clean = isbn.strip().replace("-", "").replace(" ", "")

    if not isbn_clean.isdigit() or len(isbn_clean) not in (10, 13):
        return "Error: ISBN must be a 10 or 13 digit number."

    url = f"{OPENLIBRARY_BASE_URL}/isbn/{isbn_clean}.json"

    try:
        response = requests.get(url, timeout=15)

        if response.status_code == 404:
            return f"Error: No book found with ISBN '{isbn_clean}'."

        response.raise_for_status()
        data = response.json()

        title      = data.get("title", "N/A")
        subtitle   = data.get("subtitle", "")
        publishers = ", ".join(data.get("publishers", ["N/A"]))
        publish_date = data.get("publish_date", "N/A")
        pages      = data.get("number_of_pages", "N/A")

        # Description can be a string or a dict
        desc_raw   = data.get("description", "N/A")
        description = (
            desc_raw.get("value", "N/A")
            if isinstance(desc_raw, dict)
            else str(desc_raw)
        )
        # Trim long descriptions
        if len(description) > 300:
            description = description[:300].rstrip() + "..."

        full_title = f"{title}: {subtitle}" if subtitle else title

        return (
            f"Book Details (ISBN: {isbn_clean}):\n"
            f"  Title       : {full_title}\n"
            f"  Publisher   : {publishers}\n"
            f"  Published   : {publish_date}\n"
            f"  Pages       : {pages}\n"
            f"  Description : {description}"
        )

    except requests.exceptions.ConnectionError:
        return "Error: No internet connection."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Try again."
    except Exception as e:
        return f"Error: {str(e)}"