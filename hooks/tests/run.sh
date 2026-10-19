#!/usr/bin/env bash
# Roda os testes dos guardas. Execute da raiz do repositorio.
set -e
python hooks/tests/test_guards.py
echo
python hooks/tests/test_dod_docs.py
echo
python hooks/tests/test_writing_guard.py
