def camel_case_to_snake_case(input_str: str) -> str:
    """
    >>> camel_case_to_snake_case("SomeSDK")
    'some_sdk'
    >>> camel_case_to_snake_case("RServoDrive")
    'r_servo_drive'
    >>> camel_case_to_snake_case("SDKDemo")
    'sdk_demo'
    """
    chars = []
    for c_idx, char in enumerate(input_str):
        if c_idx and char.isupper():
            nxt_idx = c_idx + 1
            # idea of the flag is to separate abbreviations
            # as new words, show them in lower case
            flag = nxt_idx >= len(input_str) or input_str[nxt_idx].isupper()
            prev_char = input_str[c_idx - 1]
            if prev_char.isupper() and flag:
                pass
            else:
                chars.append("_")
        chars.append(char.lower())
    return "".join(chars)


def to_plural(word: str) -> str:
    """Convert singular form to plural.

    >>> to_plural("category")
    'categories'
    >>> to_plural("box")
    'boxes'
    >>> to_plural("query")
    'queries'
    >>> to_plural("dish")
    'dishes'
    """
    if word.endswith("y"):
        # For words ending in 'y', replace 'y' with 'ies'
        return word[:-1] + "ies"
    elif word.endswith(("s", "sh", "ch", "x", "z")):
        # For words ending in s, sh, ch, x, or z, add 'es'
        return word + "es"
    else:
        # Default case: just add 's'
        return word + "s"


def convert_and_pluralize(input_str: str) -> str:
    """Convert from CamelCase to snake_case and pluralize.

    >>> convert_and_pluralize("Category")
    'categories'
    >>> convert_and_pluralize("BoxItem")
    'box_items'
    """
    snake_case = camel_case_to_snake_case(input_str)
    words = snake_case.split("_")
    words[-1] = to_plural(words[-1])  # Pluralize the last word
    return "_".join(words)
