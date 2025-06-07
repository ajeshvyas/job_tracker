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
