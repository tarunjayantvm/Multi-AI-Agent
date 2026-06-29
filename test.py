import requests

print("Testing restcountries.com...")
try:
    r = requests.get("https://restcountries.com/v3.1/name/India", timeout=15)
    print("Status:", r.status_code)
    print("OK!" if r.status_code == 200 else "Failed")
except Exception as e:
    print("Error:", type(e).__name__, str(e))