from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import UserLocation

location_bp = Blueprint("location", __name__)

@location_bp.route("/share-location", methods=["POST"])
def share_location():
    data = request.get_json()

    lat = data["lat"]
    lng = data["lng"]

    loc = UserLocation(
        user_id="Aeshika",
        group_id=1,
        latitude=lat,
        longitude=lng
    )

    db.session.add(loc)
    db.session.commit()

    return jsonify({"status": "location saved"})

from flask import render_template
from app.models import UserLocation

@location_bp.route("/locations")
def show_locations():

    locations = UserLocation.query.all()

    location_data = []

    for loc in locations:
        location_data.append({
            "user_id": loc.user_id,
            "latitude": loc.latitude,
            "longitude": loc.longitude
        })

    return render_template("locations.html", locations=location_data)

from flask import jsonify

@location_bp.route("/api/locations")
def api_locations():

    locations = UserLocation.query.all()

    location_data = []

    for loc in locations:
        location_data.append({
            "user_id": loc.user_id,
            "latitude": loc.latitude,
            "longitude": loc.longitude
        })

    return jsonify(location_data)




