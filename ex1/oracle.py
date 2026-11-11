from dotenv import load_dotenv
import os
import sys

load_dotenv()

MATRIX_MODE = os.getenv("MATRIX_MODE", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///oracle.db")
API_KEY = os.getenv("API_KEY", "your-api-key-here")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
ZION_ENDPOINT = os.getenv("ZION_ENDPOINT", "https://zion.example.com")


def load_config() -> None:
    req_conf: list[str] = [
        "MATRIX_MODE",
        "DATABASE_URL",
        "API_KEY",
        "LOG_LEVEL",
        "ZION_ENDPOINT",
    ]
    miss_conf: list[str] = [line for line in req_conf if line not in os.environ]
    if miss_conf:
        print(f"Error, missing configuration: {', '.join(miss_conf)}",
              file=sys.stderr)
        print("Using default values for missing configuration.")
    print("Configuration loaded:")

def show_dev() -> None:
     print("Mode: Development")
     print("Database:", DATABASE_URL)
     print("API Access: Authenticated")
     print("Log Level: DEBUG")
     print("Zion Network: ", ZION_ENDPOINT)


def show_prod() -> None:
     print("Mode: Production")
     print("Database: Connected to local instance")
     print("API Access: Authenticated")
     print("Log Level: INFO")
     print("Zion Network: Online")


def main() -> None:
    print("\nORACLE STATUS: Reading the Matrix...")
    load_config()
    if MATRIX_MODE == "development":
         show_dev()
    elif MATRIX_MODE == "production":
         show_prod()
    else:
        print(f"Warning: unknown MATRIX_MODE '{MATRIX_MODE}', "
              "defaulting to development.", file=sys.stderr)
        show_dev()


if __name__ == "__main__":
    main()