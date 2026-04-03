import os
import pandas as pd
from IPython.display import display
from google import genai
from google.genai import types
from dotenv import load_dotenv

from fields import FIELDS
from utils import (
    build_field_schema,
    load_prompt,
    clean_json,
    apply_discovery_url_overrides,
)
from validator import validate_discovery

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
MODEL = "gemini-2.5-pro"
client = genai.Client(api_key=GEMINI_API_KEY)

DISCOVERY_PROMPT = os.path.join("prompts", "discovery.txt")
EXTRACTION_PROMPT = os.path.join("prompts", "extraction.txt")


# ── Stage 1: Discover the correct program + URLs ──────────────────────────────
def discover_program(college_name: str) -> dict:
    print(f"\n[Stage 1] Discovering program for: {college_name}")

    domain_guess = college_name.lower().replace(" ", "") + ".edu"

    prompt = load_prompt(
        DISCOVERY_PROMPT,
        college_name=college_name,
        college_domain=domain_guess
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            temperature=0.1,
        ),
    )

    discovery = clean_json(response.text)
    discovery = apply_discovery_url_overrides(college_name, discovery)

    print(f"  Program found : {discovery.get('program_name')}")
    print(f"  Program URL   : {discovery.get('program_url')}")

    return discovery


# ── Stage 2: Gemini reads URLs natively via URL Context ───────────────────────
def extract_program_data(college_name: str, discovery: dict) -> dict:
    print(f"\n[Stage 2] Extracting data using URL context")

    program_url = discovery.get("program_url", "Not Found")
    tuition_url = discovery.get("tuition_url", "Not Found")
    faculty_url = discovery.get("faculty_url", "Not Found")
    admissions_url = discovery.get("admissions_url", "Not Found")

    print(f"  Program page  : {program_url}")
    print(f"  Tuition page  : {tuition_url}")
    print(f"  Faculty page  : {faculty_url}")
    print(f"  Admissions    : {admissions_url}")

    prompt = load_prompt(
        EXTRACTION_PROMPT,
        college_name=college_name,
        program_name=discovery.get("program_name", "Unknown"),
        program_url=program_url,
        tuition_url=tuition_url,
        faculty_url=faculty_url,
        admissions_url=admissions_url,
        schema=build_field_schema()
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[{"url_context": {}}],
            temperature=0.1,
        ),
    )

    return clean_json(response.text)


# ── Build DataFrame ───────────────────────────────────────────────────────────
def build_dataframe(data: dict) -> pd.DataFrame:
    row = {}

    for key, label, _ in FIELDS:
        field = data.get(key, {})
        if isinstance(field, dict):
            value = field.get("value", "Not Found")
        else:
            value = str(field)

        row[label] = value

    return pd.DataFrame([row])


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    college_name = input(
        "Enter the college name (e.g., 'Stanford University'): "
    ).strip()

    college_target = college_name
    slug = college_target.replace(" ", "_").lower()
    output_dir = os.path.join("outputs", slug)
    os.makedirs(output_dir, exist_ok=True)
    discovery_path = os.path.join(output_dir, f"{slug}_discovery.csv")

    # Stage 1: Discover
    discovery = discover_program(college_target)

    is_valid, reason = validate_discovery(discovery)
    if not is_valid:
        discovery_record = dict(discovery)
        discovery_record["validation_status"] = "Invalid"
        discovery_record["validation_reason"] = reason
        pd.DataFrame([discovery_record]).to_csv(discovery_path, index=False)

        print(f"\nInvalid program detected: {reason}")
        print(f"Discovery saved to: {discovery_path}")
        print("\nNo CSV generated because no valid non-degree certificate was found.")
        exit(0)

    print(f"\nValidated program: {discovery['program_name']}")

    # Stage 2: Extract
    extracted_json = extract_program_data(college_target, discovery)

    # Build DataFrame
    df = build_dataframe(extracted_json)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", 80)
    display(df.T)

    # Save output
    data_path = os.path.join(output_dir, f"{slug}_cybersecurity_full.csv")

    df.to_csv(data_path, index=False)
    print(f"\nData saved to: {data_path}")

    discovery_record = dict(discovery)
    discovery_record["validation_status"] = "Valid"
    discovery_record["validation_reason"] = reason
    pd.DataFrame([discovery_record]).to_csv(discovery_path, index=False)
    print(f"Discovery saved to: {discovery_path}")