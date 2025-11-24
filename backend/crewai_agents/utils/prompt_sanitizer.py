import re

def sanitize_for_llm_prompt(text: str) -> str:
    """
    Sanitizes user-supplied text to prevent prompt injection.
    Removes or neutralizes common LLM instruction keywords and markdown.
    """
    if not isinstance(text, str):
        return str(text)

    # Basic neutralization: replace newline characters to prevent multi-line instruction injection
    text = text.replace('\n', ' ').replace('\r', ' ')

    # Neutralize common instruction-like keywords
    # This is a heuristic and not foolproof, but helps against common attacks
    instruction_keywords = [
        "ASSISTANT:", "USER:", "SYSTEM:", "ROLEPLAY:", "IGNORE:", "DISREGARD:",
        "INSTRUCT:", "COMMAND:", "EXECUTE:", "RESPOND AS:", "DO NOT:",
        "PRETEND TO BE:", "ACT AS:", "IMPORTANT:", "SECURITY:", "JAILBREAK:",
        "PROMPT:", "OVERRIDE:", "URGENT:", "CRITICAL:"
    ]
    for keyword in instruction_keywords:
        text = text.replace(keyword, re.sub(r'\w', '_', keyword)) # Replace with underscores

    # Neutralize markdown-like characters that could break prompt structure
    text = re.sub(r'\[.*?\]', lambda m: m.group(0).replace('[', '(').replace(']', ')'), text) # Replace brackets in links etc.
    text = text.replace('```', "'''") # Code block delimiters
    text = text.replace('---', "___") # Horizontal rule/list item delimiters
    text = text.sub(r'#+\s', '', text) # Remove # for headers

    # Enclose the text within data-specific delimiters as a defense-in-depth measure
    # This assumes the LLM has been instructed to treat content within these tags as data, not instructions
    return f"<RAG_CONTEXT_START>{text}</RAG_CONTEXT_END>"
