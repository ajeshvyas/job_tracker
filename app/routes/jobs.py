from flask import Blueprint, request, jsonify, g
from app import db
from app.models import Company, JobApplication
from app.decorators import jwt_required

jobs_bp = Blueprint("jobs", __name__)

@jobs_bp.route("/companies", methods=["POST"])
@jwt_required
def create_company():
    data = request.json
    company = Company(
        name=data["name"],
        industry=data.get("industry"),
        location=data.get("location")
    )
    db.session.add(company)
    db.session.commit()
    return jsonify({"message": "Company created", "company_id": company.id}), 201

@jobs_bp.route("/applications", methods=["POST"])
@jwt_required
def create_application():
    data = request.json
    appn = JobApplication(
        role=data["role"],
        company_id=data["company_id"],
        user_id=g.current_user.id,
        status=data.get("status", "Applied"),
        notes=data.get("notes")
    )
    db.session.add(appn)
    db.session.commit()
    return jsonify({"message": "Job application added", "application_id": appn.id}), 201

@jobs_bp.route("/applications", methods=["GET"])
@jwt_required
def get_my_applications():
    apps = JobApplication.query.filter_by(user_id=g.current_user.id).all()
    return jsonify([
        {
            "id": a.id,
            "role": a.role,
            "status": a.status,
            "company": a.company.name,
            "applied_date": a.applied_date.isoformat(),
            "notes": a.notes
        } for a in apps
    ])

# Update status or notes
@jobs_bp.route("/applications/<int:id>", methods=["PUT"])
@jwt_required
def update_application(id):
    appn = JobApplication.query.filter_by(id=id, user_id=g.current_user.id).first()
    if not appn:
        return jsonify({"error": "Application not found"}), 404

    data = request.json
    if "status" in data:
        appn.status = data["status"]
    if "notes" in data:
        appn.notes = data["notes"]
    db.session.commit()
    return jsonify({"message": "Application updated"})

# Delete application
@jobs_bp.route("/applications/<int:id>", methods=["DELETE"])
@jwt_required
def delete_application(id):
    appn = JobApplication.query.filter_by(id=id, user_id=g.current_user.id).first()
    if not appn:
        return jsonify({"error": "Application not found"}), 404

    db.session.delete(appn)
    db.session.commit()
    return jsonify({"message": "Application deleted"})

