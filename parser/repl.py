import sys
import os
from pprint import pprint

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.database import Database


PROMPT = "rdbms> "


def print_result(result):
    """Pretty-print query results"""
    if result is None:
        print("OK")
    elif isinstance(result, list):
        if not result:
            print("(no rows)")
        else:
            for row in result:
                pprint(row)
            print(f"\n({len(result)} rows)")
    else:
        print(result)


def print_help():
    print("""
Supported commands:
-------------------
CREATE TABLE ...
DROP TABLE ...
INSERT INTO ...
SELECT ...
UPDATE ...
DELETE ...
CREATE INDEX ...
DROP INDEX ...

Special commands:
-----------------
.help      Show this help
exit      Exit the REPL
quit      Exit the REPL
quit();   Exit the REPL
exit();   Exit the REPL          
""")


def start_repl():
    print("Simple RDBMS REPL")
    print("Type help for help, exit,exit();,quit or quit(); to quit\n")

    db = Database()

    buffer = ""

    while True:
        try:
            line = input(PROMPT).strip()

            # Handle special commands
            if line in ("exit", "quit","exit();","quit();"):
                print("Bye!")
                break

            if line.lower() in ("help", ".help"):
                print_help()
                continue

            if not line:
                continue

            # Support multi-line SQL until semicolon
            buffer += " " + line
            if not buffer.strip().endswith(";"):
                continue

            query = buffer.strip().rstrip(";")
            buffer = ""

            result = db.execute_query(query)
            print_result(result)

        except KeyboardInterrupt:
            print("\nInterrupted. Type .exit to quit.")
            buffer = ""
        except Exception as e:
            print(f"Error: {e}")
            buffer = ""


if __name__ == "__main__":
    start_repl()
