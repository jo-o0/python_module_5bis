from .dark_validator import validate_ingredients as validate


def dark_spell_allowed_ingredients() -> list[str]:
    return["bats", "frogs", "arsenic", "eyeball"]


def dark_spell_record(spell_name: str, ingredients: str) -> str:
    result: str = validate(ingredients)
    if "VALID" in result:
        return f"{spell_name} RECORDED"
    else:
        return f"{spell_name} NOT RECORDED"