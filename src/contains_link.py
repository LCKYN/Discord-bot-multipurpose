import re


def contains_link(text_input):
    url_pattern = re.compile(
        r"http[s]?://" r"(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|" r"(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        re.IGNORECASE,
    )
    return re.search(url_pattern, text_input) is not None
