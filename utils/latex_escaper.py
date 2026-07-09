import re

def escape_latex(text: str) -> str:
    if not isinstance(text, str):
        return text

    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }

    escaped_text = text
    for char, replacement in special_chars.items():
        escaped_text = re.sub(r'(?<!\\)' + re.escape(char), replacement, escaped_text)

    escaped_text = re.sub(r'(?<!\\)\|', r'$|$', escaped_text)
    return escaped_text

def escape_latex_recursive(data: any) -> any:
    if isinstance(data, str):
        return escape_latex(data)
    elif isinstance(data, list):
        return [escape_latex_recursive(item) for item in data]
    elif isinstance(data, dict):
        return {key: escape_latex_recursive(val) for key, val in data.items()}
    return data
