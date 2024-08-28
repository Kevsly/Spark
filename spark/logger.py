import logging.handlers


# This is only used with console_handler, check out the other commented out lines
class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1B[38;5;16m"
    dark_red = "\x1B[38;5;88m"
    red = "\x1B[38;5;196m"
    green = "\x1B[38;5;40m"
    yellow = "\x1B[38;5;220m"
    blue = "\x1B[38;5;27m"
    gray = "\x1B[38;5;237m"

    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"
    italic = "\x1b[3m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red + bold,
        logging.CRITICAL: dark_red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        formatted = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (italic)(green){name}(reset) {message}"
        formatted = formatted.replace("(black)", self.black + self.bold)
        formatted = formatted.replace("(reset)", self.reset)
        formatted = formatted.replace("(levelcolor)", log_color)
        formatted = formatted.replace("(italic)", self.italic)
        formatted = formatted.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(formatted, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


file_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)

root_logger = logging.getLogger("Spark")
root_logger.setLevel(logging.DEBUG)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())

# File Handler
file_handler = logging.handlers.TimedRotatingFileHandler(
    filename="spark/logs/spark.log",
    when="midnight",
    interval=1,
    backupCount=5,
    encoding="utf-8",
)
file_handler.setFormatter(file_formatter)

# Add the handlers
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)
