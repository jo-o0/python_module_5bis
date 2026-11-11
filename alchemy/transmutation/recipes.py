from ..elements import create_air
from elements import create_fire
from alchemy.potions import strength_potion

def lead_to_gold() -> str:
    header: str = "Recipe transmuting Lead to Gold: "
    brew: str = f"brew '{create_air()}' and '{strength_potion()}'"
    mix: str = f" mixed with '{create_fire()}'"
    result: str = header + brew + mix
    return result