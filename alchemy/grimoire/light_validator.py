def validate_ingredients(ingredients: str) -> str:
    from .light_spellbook import light_spell_allowed_ingredients as allow
    allowed_list: list[str] = allow()
    user_ingredients: list[str] = [ing.strip().lower() for ing in ingredients.split(",")]
    for user_ing in user_ingredients:
        if user_ing in allowed_list:
            return f"{ingredients} VALID"
    return f"{ingredients} INVALID"