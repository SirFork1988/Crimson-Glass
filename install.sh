#!/bin/sh
set -eu
cd -- "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
    case " $* " in *' --dry-run '*|*' --help '*) printf '%s\n' 'Python 3.10+ is required. Install python/python3 with your package manager.'; exit 1;; esac
    if command -v pacman >/dev/null 2>&1; then sudo pacman -S --needed python
    elif command -v apt-get >/dev/null 2>&1; then sudo apt-get update; sudo apt-get install python3
    elif command -v dnf >/dev/null 2>&1; then sudo dnf install python3
    else printf '%s\n' 'Install Python 3.10+ first.'; exit 1
    fi
fi
exec python3 ./install.py "$@"
