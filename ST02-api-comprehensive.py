# ST02-api-comprehensive.py
# ===================================================
# Zip Code Range Report
# API: https://api.zippopotam.us/us/<zip>
#
# User Requirement:
# Allow a user to enter range of zip codes they are interested in (from and to).
# Make API calls to capture the data and extract all pieces of information from
# the returned JSON payload. Place all data in a 2D List. Generate a report with
# the data properly formatted. Check the HTTP status code in case a value in the
# range is invalid.

# Decomposing the Requirement:
# 1. Ask the user for a range of zip codes (from / to)
# 2. Call the API once per zip code in the range
# 3. Check the HTTP status code (404 = zip not found)
# 4. Extract every field from the JSON payload into a 2D list
# 5. Print a formatted report
# ===================================================

import requests

BASE_URL = "https://api.zippopotam.us/us/"
MAX_RANGE = 100  # limit the number of calls we send to a free API
TIMEOUT = 10  # seconds to wait before giving up on one call

HEADERS = [
    "Zip",
    "Country",
    "Abbr",
    "Place Name",
    "State",
    "St",
    "Latitude",
    "Longitude",
]


# -----------------------------
# Get and validate user input
# -----------------------------
def get_zip(prompt):
    """Keep asking until the user types a valid 5-digit zip code."""
    while True:
        value = input(prompt).strip()
        if value.isdigit() and len(value) == 5:
            return int(value)
        print("  Please enter exactly 5 digits (e.g. 76798).")


def get_zip_range():
    while True:
        start = get_zip("Enter the FROM zip code: ")
        end = get_zip("Enter the TO zip code:   ")

        if start > end:  # let the user type them in any order
            start, end = end, start

        count = end - start + 1
        if count > MAX_RANGE:
            print(
                f"  That range has {count} zip codes. Keep it to {MAX_RANGE} or fewer.\n"
            )
            continue
        return start, end


# -----------------------------
# Call the API for one zip code
# -----------------------------
def fetch_zip(zip_code):
    """Return (status_code, data_dict). data_dict is None if the call failed."""
    url = BASE_URL + zip_code

    # Step 1: Call the API
    response = requests.get(url, timeout=TIMEOUT)

    # Check the HTTP status code before trusting the payload
    if response.status_code != 200:
        return response.status_code, None

    # Step 2: Convert the JSON payload to a dictionary
    return response.status_code, response.json()


# -----------------------------
# Step 3: Consume the payload -> rows in a 2D list
# -----------------------------
def payload_to_rows(data):
    """
    One zip code can cover several places, so "places" is a list.
    We write one row per place and repeat the zip-level fields on each row.
    """
    rows = []
    for place in data["places"]:
        rows.append(
            [
                data["post code"],
                data["country"],
                data["country abbreviation"],
                place["place name"],
                place["state"],
                place["state abbreviation"],
                place["latitude"],
                place["longitude"],
            ]
        )
    return rows


# -----------------------------
# Generate the report
# -----------------------------
def print_report(table, invalid, start, end):
    print()
    print("=" * 92)
    print(f"ZIP CODE REPORT: {start:05d} to {end:05d}".center(92))
    print("=" * 92)

    if table:
        fmt = "{:<7}{:<16}{:<6}{:<22}{:<16}{:<5}{:>10}{:>10}"
        print(fmt.format(*HEADERS))
        print("-" * 92)
        for row in table:
            print(fmt.format(*row))
    else:
        print("No valid zip codes were found in this range.")

    print("-" * 92)
    print(f"Valid records:      {len(table)}")
    print(f"Invalid zip codes:  {len(invalid)}")

    if invalid:
        print("\nZip codes that could not be retrieved:")
        for zip_code, reason in invalid:
            print(f"  {zip_code}  ->  {reason}")
    print("=" * 92)


# -----------------------------
# Main program
# -----------------------------
def main():
    start, end = get_zip_range()

    table = []  # 2D list: each inner list is one row of the report
    invalid = []  # list of (zip, reason) for zips that failed

    print(f"\nLooking up {end - start + 1} zip code(s)...")

    for number in range(start, end + 1):
        zip_code = f"{number:05d}"  # keeps leading zeros, e.g. 00501

        try:
            status, data = fetch_zip(zip_code)
        except requests.exceptions.RequestException as err:
            invalid.append((zip_code, f"connection error ({type(err).__name__})"))
            continue

        if status == 200:
            table.extend(payload_to_rows(data))
        elif status == 404:
            invalid.append((zip_code, "404 Not Found (not a valid US zip)"))
        else:
            invalid.append((zip_code, f"HTTP {status}"))

    print_report(table, invalid, start, end)


if __name__ == "__main__":
    main()
