BOOTCAMP_KEYWORDS = [
    "bootcamp", "boot camp", "workforce", "continuing education",
    "professional development", "corporate training", "non-credit",
    "noncredit", "workforce development"
]

DEGREE_KEYWORDS = [
    "bachelor", "master of science", "master of arts", "mba",
    "associate degree", "doctoral", "phd", "m.s.", "b.s."
]

VALID_TYPES = ["graduate certificate", "undergraduate certificate"]


def validate_discovery(discovery: dict) -> tuple[bool, str]:
    """
    Returns (is_valid, reason).
    Checks that Gemini found a real academic non-degree certificate.
    """
    if discovery.get("is_valid_certificate", "").lower() != "yes":
        return False, discovery.get("rejection_reason", "Gemini flagged as invalid")

    program_name = discovery.get("program_name", "").lower()
    program_type = discovery.get("program_type", "").lower()

    for kw in BOOTCAMP_KEYWORDS:
        if kw in program_name:
            return False, f"Program name contains excluded keyword: '{kw}'"

    for kw in DEGREE_KEYWORDS:
        if kw in program_name:
            return False, f"Program name contains degree keyword: '{kw}'"

    if not any(vt in program_type for vt in VALID_TYPES):
        return False, f"Program type '{program_type}' is not a valid certificate type"

    return True, "OK"