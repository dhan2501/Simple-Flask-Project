from flask import Blueprint, jsonify
from models import Banner  # from your models.py
from db import db


banner_api = Blueprint("banner_api", __name__)

@banner_api.route("/api/banner", methods=["GET"])
def get_banner():
    banner = Banner.query.first()
    if not banner:
        return jsonify({"error": "No banner found"}), 404

    return jsonify({
        "id": banner.id,
        "id": banner.id,
        "image_url": f"/static/uploads/{banner.image_url}",
        "heading": banner.heading,
        "text": banner.text,
        "button_text": banner.button_text,
        "button_link": banner.button_link
    })
