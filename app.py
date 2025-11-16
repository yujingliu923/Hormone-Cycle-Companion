from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from calculator import calculate_cycle_details

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/evaluate", methods=["POST"])
def api_evaluate():
    payload = request.get_json() or {}

    try:
        cycle_length = int(payload.get("cycle_length") or 28)
        menses_days = int(payload.get("menses_days") or 5)
    except ValueError:
        return jsonify({"error": "周期长度与经期天数需要是数字。"}), 400

    try:
        result = calculate_cycle_details(
            payload.get("last_date"),
            observation_date=payload.get("target_date"),
            cycle_length=cycle_length,
            menses_days=menses_days,
            role=(payload.get("role") or "self"),
            tone=(payload.get("tone") or "gentle"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
