import os
from flask import Flask, jsonify

app = Flask(__name__)

BASES = [
    os.getcwd(),
    os.path.join(os.path.dirname(__file__), ".."),
    os.path.dirname(__file__),
]
def _resolve_logos_root():
    for base in BASES:
        cand = os.path.abspath(os.path.join(base, 'logos'))
        if os.path.isdir(cand):
            return cand
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logos'))
LOGOS_ROOT = _resolve_logos_root()

@app.get("/")
@app.get("/languages")
def languages():
    langs = []
    if os.path.isdir(LOGOS_ROOT):
        for name in os.listdir(LOGOS_ROOT):
            p = os.path.join(LOGOS_ROOT, name)
            if os.path.isdir(p):
                langs.append(name)
    langs.sort()
    return jsonify({"languages": langs})
