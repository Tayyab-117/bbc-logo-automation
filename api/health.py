from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/")
@app.get('/api/health')
@app.get("/health")
def health():
    return jsonify({"ok": True})
