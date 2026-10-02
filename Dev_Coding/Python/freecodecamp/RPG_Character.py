def create_character(name, strength, intelligence, charisma):
    if type(name) is not str:
        return "The character name should be a string."
    if name == "":
        return "The character should have a name."
    if len(name) > 10:
        return "The character name is too long."
    if " " in name:
        return "The character name should not contain spaces."
        
    if type(strength) is not int or type(intelligence) is not int or type(charisma) is not int:
        return "All stats should be integers."
    if strength < 1 or intelligence < 1 or charisma < 1:
        return "All stats should be no less than 1."
    if strength > 4 or intelligence > 4 or charisma > 4:
        return "All stats should be no more than 4."
    if strength + intelligence + charisma != 7:
        return "The character should start with 7 points."
        
    str_line = f"STR {'●' * strength}{'○' * (10 - strength)}"
    int_line = f"INT {'●' * intelligence}{'○' * (10 - intelligence)}"
    cha_line = f"CHA {'●' * charisma}{'○' * (10 - charisma)}"
    
    return f"{name}\n{str_line}\n{int_line}\n{cha_line}"

print(create_character("Haz", 2, 3, 2))