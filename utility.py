#evaluates select options and returns matching number
def evaluate_select(var, options : list[str], default_value = 1) -> int:
    for i in range(len(options)):
        if (var == options[i]):
            return i + 1
    return default_value


