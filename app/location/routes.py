from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user

from app.extensions import db
from app.models import UserLocation, User

location_bp = Blueprint("location", __name__, url_prefix="/location")


# -------- Location Page --------
@location_bp.route("/<int:group_id>")
@login_required
def location_page(group_id):
    return render_template("location.html", group_id=group_id)


# -------- Save Location --------
@location_bp.route("/share-location/<int:group_id>", methods=["POST"])
@login_required
def share_location(group_id):

    data = request.get_json()

    lat = data["lat"]
    lng = data["lng"]

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

    return jsonify({"status":"saved"})


# -------- Get Locations --------
@location_bp.route("/api/<int:group_id>")
@login_required
def api_locations(group_id):

    locations = UserLocation.query.filter_by(group_id=group_id).all()

    data = []

    for loc in locations:

        user = User.query.get(loc.user_id)

        data.append({
            "user_id":loc.user_id,
            "username":user.username,
            "profile_picture":f"/static/profile_pics/{user.profile_picture}" if user.profile_picture else "/static/profile_pics/default.png",
            "latitude":loc.latitude,
            "longitude":loc.longitude
        })

    return jsonify(data)