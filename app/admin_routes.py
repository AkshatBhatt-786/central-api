from flask import Blueprint, request, jsonify, render_template
from app.models import get_all_organizations, create_organization

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def admin_dashboard():
    return render_template('admin_dashboard/index.html')


@admin_bp.route('/api/organizations', methods=['GET'])
def get_orgs_api():
    try:
        organizations = get_all_organizations()
        return jsonify({"success": True, "organizations": organizations})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/api/organizations', methods=['POST'])
def create_org_api():
    try:
        data = request.get_json()
        result = create_organization(
            org_id=data['org_id'],
            org_name=data['name'],
            contact_email=data.get('contact_email', ''),
            tier=data['tier'],
            license_name=data['license_name']
        )
        if result:
            return jsonify({"success": True, "organization": result})
        else:
            return jsonify({"success": False, "error": "Failed to create organization"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500