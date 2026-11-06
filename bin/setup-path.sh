#!/bin/sh
# Acrescenta (ou remove com --remove) a pasta bin/ ao PATH em ~/.bashrc e ~/.zshrc existentes.
BEGIN="# >>> bkhar >>>"
END="# <<< bkhar <<<"
BIN="$(cd "$(dirname "$0")" && pwd)"
RC_DIR="$HOME"
REMOVE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --remove) REMOVE=1 ;;
    --rc-dir) shift; RC_DIR="$1" ;;
    *) echo "uso: setup-path.sh [--remove] [--rc-dir DIR]" >&2; exit 2 ;;
  esac
  shift
done

strip_block() {
  awk -v b="$BEGIN" -v e="$END" '$0==b{skip=1;next} $0==e{skip=0;next} !skip' "$1" > "$1.bkhar.tmp" && mv "$1.bkhar.tmp" "$1"
}

for name in .bashrc .zshrc; do
  rc="$RC_DIR/$name"
  [ -f "$rc" ] || continue
  strip_block "$rc"
  if [ "$REMOVE" -eq 0 ]; then
    printf '%s\nexport PATH="%s:$PATH"\n%s\n' "$BEGIN" "$BIN" "$END" >> "$rc"
    echo "PATH acrescentado em $rc"
  else
    echo "bloco removido de $rc"
  fi
done
