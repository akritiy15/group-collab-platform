from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user

from app.extensions import db
from app.models import UserLocation

location_bp = Blueprint("location", __name__, url_prefix="/location")


# ---------------- LOCATION PAGE ----------------
@location_bp.route("/<int:group_id>")
@login_required
def location_page(group_id):
    return render_template("location.html", group_id=group_id)


# ---------------- SAVE LOCATION ----------------
@location_bp.route("/share-location/<int:group_id>", methods=["POST"])
@login_required
def share_location(group_id):

    data = request.get_json()

    lat = data["lat"]
    lng = data["lng"]

    # check if already exists
    loc = UserLocation.query.filter_by(
        user_id=current_user.id,
        group_id=group_id
    ).first()

    if loc:
        loc.latitude = lat
        loc.longitude = lng
    else:
        loc = UserLocation(
            user_id=current_user.id,
            group_id=group_id,
            latitude=lat,
            longitude=lng
        )
        db.session.add(loc)

    db.session.commit()

    return jsonify({"status": "saved"})


# ---------------- API GET LOCATIONS ----------------
@location_bp.route("/api/<int:group_id>")
@login_required
def api_locations(group_id):

    locations = UserLocation.query.filter_by(group_id=group_id).all()

    location_data = []

    for loc in locations:
        location_data.append({
            "user_id": loc.user_id,
            "latitude": loc.latitude,
            "longitude": loc.longitude
        })

    return jsonify(location_data)