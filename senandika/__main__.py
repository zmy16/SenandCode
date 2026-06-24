"""
Entry point utama SenandCode.

Cara menjalankan:
  senandika program.sen
  python -m senandika program.sen
  python -m senandika          # REPL mode
"""

import sys
import os
import io
import argparse

# Fix Windows console encoding for Unicode
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from senandika.lexer import Lexer
from senandika.parser import Parser
from senandika.interpreter import Interpreter


def repl():
    """Interactive REPL dengan state yang dipertahankan."""
    print("✦ SenandCode v0.1.0 🌸")
    print("  Setiap baris adalah puisi.")
    print('  Ketik "selesai" untuk keluar.\n')

    interpreter = Interpreter([])

    while True:
        try:
            code = input("✦ ").strip()
            if not code:
                continue
            if code.lower() in ("selesai", "keluar", "exit", "quit"):
                print("  Sampai jumpa dalam puisi berikutnya... 🌸")
                break

            # Auto-append semicolon if the statement doesn't already end with one
            # and isn't a block-starting keyword that expects ':'
            repl_no_semi = ("seandainya", "atau", "jika", "untuk", "selagi", "puisi", "wajah", "coba", "raih", "akhirnya", "selesai")
            stripped = code.strip()
            if not stripped.endswith(";") and not stripped.endswith(":"):
                first_word = stripped.split()[0].lower() if stripped else ""
                if first_word not in repl_no_semi and not stripped.startswith("*"):
                    code += ";"

            lexer = Lexer(code)
            tokens = list(lexer.tokenize())
            if not tokens:
                continue

            parser_obj = Parser(tokens)
            ast = parser_obj.parse()

            interpreter.execute(ast)

        except KeyboardInterrupt:
            print("\n  Sampai jumpa 🌸")
            break
        except EOFError:
            print("\n  Sampai jumpa 🌸")
            break
        except Exception as e:
            print(f"  ✗ {e}")


def main():
    parser = argparse.ArgumentParser(
        prog="senandika",
        description="SenandCode - Bahasa pemrograman puitis dalam Bahasa Indonesia 🌸",
        epilog="Contoh: senandika contoh/halo.sen",
    )
    parser.add_argument("file", nargs="?", help="File .sen yang akan dijalankan")
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="SenandCode v0.1.0",
    )

    args = parser.parse_args()
    filename = args.file

    if not filename:
        repl()
        return

    if not os.path.exists(filename):
        print(f"  ✗ Puisi '{filename}' tak kutemukan...")
        sys.exit(1)

    if not filename.endswith(".sen"):
        print("  ✗ Berkas haruslah berakhiran .sen")
        sys.exit(1)

    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        lexer = Lexer(code)
        tokens = list(lexer.tokenize())

        parser_obj = Parser(tokens)
        ast = parser_obj.parse()

        interpreter = Interpreter(ast)
        interpreter.interpret()

    except SyntaxError as e:
        print(f"  ✗ Indah namun tak terbaca: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"  ✗ Terjadi kesalahan saat membaca puisi: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  ✗ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
