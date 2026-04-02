import json
import re
from fields import FIELDS


_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


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