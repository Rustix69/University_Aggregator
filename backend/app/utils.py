import json
import re
from fields import FIELDS


_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

_CANONICAL_DISCOVERY_URLS = {
    "trident technical college": {
        "program_url": "https://www.tridenttech.edu/programs/divisions/bt/cybersecurity.html",
        "tuition_url": "https://www.tridenttech.edu/cost/tuition.html",
        "faculty_url": "https://www.tridenttech.edu/programs/divisions/bt/center_for_cybersecurity/faculty.html",
        "admissions_url": "https://www.tridenttech.edu/admissions/index.html",
    }
}


def build_field_schema() -> str:
    schema = []
    for key, _, _ in FIELDS:
        schema.append(f'    "{key}": {{"value": "..."}}')
    return ",\n".join(schema)


def load_prompt(path: str, **kwargs) -> str:
    with open(path, "r", encoding="utf-8") as f:
        template = f.read()

    # Replace only named placeholders like {college_name} and leave JSON braces intact.
    def replace_placeholder(match: re.Match) -> str:
        key = match.group(1)
        return str(kwargs.get(key, match.group(0)))

    rendered = _PLACEHOLDER_RE.sub(replace_placeholder, template)

    # Support legacy prompts that used escaped braces for str.format-style templates.
    rendered = rendered.replace("{{", "{").replace("}}", "}")

    return rendered


def clean_json(raw_text: str) -> dict:
    raw_text = raw_text.strip()

    # Strip markdown fences
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw_text = "\n".join(lines).strip()

    start = raw_text.find("{")
    end   = raw_text.rfind("}")

    if start == -1 or end == -1:
        print("Failed JSON Text:", raw_text)
        raise ValueError("No valid JSON object found in model response")

    json_str = raw_text[start:end + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Direct parse failed ({e}), attempting recovery...")

    try:
        decoder = json.JSONDecoder()
        obj, _ = decoder.raw_decode(json_str)
        return obj
    except json.JSONDecodeError as e:
        print("Recovery failed. Raw snippet:")
        print(json_str[:500])
        raise ValueError(f"Could not parse JSON: {e}")


def _normalize_college_name(college_name: str) -> str:
    return " ".join(str(college_name or "").strip().lower().split())


def apply_discovery_url_overrides(college_name: str, discovery: dict) -> dict:
    """
    Normalize known institutions to current canonical URLs.
    Some school websites keep legacy paths live in search results even when they 404.
    """
    normalized_name = _normalize_college_name(college_name)
    overrides = _CANONICAL_DISCOVERY_URLS.get(normalized_name)

    if not overrides:
        return discovery

    merged = dict(discovery)
    for key, value in overrides.items():
        merged[key] = value

    return merged