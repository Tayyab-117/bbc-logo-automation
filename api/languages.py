import os
from flask import Flask, jsonify

app = Flask(__name__)

LOGOS_ROOT = os.path.join(os.path.dirname(__file__), "..", "logos")

@app.route("/api/languages")
def languages():
    langs = []
    if os.path.isdir(LOGOS_ROOT):
        for name in os.listdir(LOGOS_ROOT):
            p = os.path.join(LOGOS_ROOT, name)
            if os.path.isdir(p):
                langs.append(name)
    langs.sort()
    return jsonify({"languages": langs})

# Local run for testing only
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
