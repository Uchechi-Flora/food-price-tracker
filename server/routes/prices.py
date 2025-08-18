from flask import Blueprint, jsonify

prices_bp = Blueprint("prices", __name__)

# Temporary test route
@prices_bp.route("/", methods=["GET"])
def get_prices():
    return jsonify({
        "item": "50kg Rice",
        "prices": [
            {"source": "PricePally", "price": 47000},
            {"source": "Jumia", "price": 48000}
        ]
    })
