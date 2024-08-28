CHECK = "<:check:1278189910863646803>"
CROSS = "<:cross:1278189921793740812>"
WARNING = "<:warning:1278189944698835005>"
ERROR = "<:error:1278189930996043921>"
# PLUS = "<:plus:> "
# MINUS = "<:minus:>"


def success(message: str) -> str:
    return f"{CHECK} {message}"


def fail(message: str) -> str:
    return f"{CROSS} {message}"


def warn(message: str) -> str:
    return f"{WARNING} {message}"


def error(message: str) -> str:
    return f"{ERROR} {message}"


# def grant(message: str) -> str:
#     return f"{PLUS} {message}"
#
#
# def revoke(message: str) -> str:
#     return f"{MINUS} {message}"
