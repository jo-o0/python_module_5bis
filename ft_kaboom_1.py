print("=== Kaboom 1 ===")
try:
    from alchemy.grimoire.dark_spellbook import dark_spell_record 
    print(dark_spell_record("Fantasy", "Fire"))
except Exception as e:
    print("...The lab has exploted lol\n", e)
