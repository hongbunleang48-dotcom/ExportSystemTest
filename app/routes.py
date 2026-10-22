"""app/routes.py

Web & API routes for the Clinical Triage Expert System.
Handles GET and POST for form-based triage, RESTful JSON evaluation,
and lightweight bilingual locale switching (/lang/<string:locale>).
"""

from __future__ import annotations

from typing import Any, Dict

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from app.core.engine import InferenceEngine
from app.core.i18n import SUPPORTED_LOCALES, DEFAULT_LOCALE
from app.core.rules import get_knowledge_base

main_bp = Blueprint("main", __name__)


def _extract_form_facts(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts and parses facts submitted from the HTML web form."""
    facts: Dict[str, Any] = {}

    # Temperature
    temp_str = form_data.get("temperature", "").strip()
    try:
        facts["temperature"] = float(temp_str) if temp_str else 37.0
    except ValueError:
        facts["temperature"] = 37.0

    # Duration
    dur_str = form_data.get("duration_days", "").strip()
    try:
        facts["duration_days"] = int(dur_str) if dur_str else 1
    except ValueError:
        facts["duration_days"] = 1

    # Oxygen Saturation (optional)
    spo2_str = form_data.get("oxygen_saturation", "").strip()
    if spo2_str:
        try:
            facts["oxygen_saturation"] = float(spo2_str)
        except ValueError:
            facts["oxygen_saturation"] = None
    else:
        facts["oxygen_saturation"] = None

    # Categorical strings
    facts["cough_severity"] = form_data.get("cough_severity", "none").strip().lower()
    facts["respiratory_distress"] = form_data.get("respiratory_distress", "none").strip().lower()

    # Checkbox boolean indicators
    facts["chest_pain"] = "chest_pain" in form_data
    facts["lethargy_confusion"] = "lethargy_confusion" in form_data
    facts["high_risk_condition"] = "high_risk_condition" in form_data

    return facts


@main_bp.route("/lang/<string:locale>", methods=["GET"])
def set_language(locale: str):
    """Switches the session language preference between English ('en') and Khmer ('km').
    
    Saves the selected language in session['locale'] and redirects back to the previous page.
    """
    if locale in SUPPORTED_LOCALES:
        session["locale"] = locale
    # Redirect back to previous referrer or fall back to home index
    next_url = request.referrer or url_for("main.index")
    return redirect(next_url)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    """Renders the diagnostic triage form (GET) or evaluates submitted patient facts (POST)."""
    engine = InferenceEngine()
    result = None
    inputs: Dict[str, Any] = {
        "temperature": 37.0,
        "cough_severity": "none",
        "respiratory_distress": "none",
        "duration_days": 1,
        "oxygen_saturation": "",
        "chest_pain": False,
        "lethargy_confusion": False,
        "high_risk_condition": False,
    }

    if request.method == "POST":
        try:
            facts = _extract_form_facts(request.form)
            inputs.update(facts)
            result = engine.evaluate(facts)
        except Exception as exc:
            flash(f"Error during triage evaluation: {str(exc)}", "danger")

    return render_template("index.html", result=result, inputs=inputs)


@main_bp.route("/api/evaluate", methods=["POST"])
def api_evaluate():
    """RESTful API endpoint evaluating patient facts passed via JSON.
    
    Expected JSON payload:
    {
        "temperature": float (e.g. 39.2),
        "cough_severity": string ("none"|"mild"|"moderate"|"severe"),
        "respiratory_distress": string ("none"|"mild"|"moderate"|"severe"),
        "duration_days": int (e.g. 4),
        "oxygen_saturation": optional float (e.g. 91.0),
        "chest_pain": optional bool,
        "lethargy_confusion": optional bool,
        "high_risk_condition": optional bool
    }
    
    Returns:
        JSON response with final deduction, audit trail, and working memory.
    """
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Content-Type must be 'application/json'",
        }), 400

    payload = request.get_json(silent=True)
    if payload is None or not isinstance(payload, dict):
        return jsonify({
            "status": "error",
            "message": "Malformed JSON body; must be a valid JSON object.",
        }), 400

    try:
        engine = InferenceEngine()
        result = engine.evaluate(payload)
        return jsonify({
            "status": "success",
            "data": result.to_dict(),
        }), 200
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": f"Inference execution failure: {str(exc)}",
        }), 500


@main_bp.route("/api/rules", methods=["GET"])
def api_rules():
    """Returns the complete knowledge base rule definitions."""
    rules = get_knowledge_base()
    return jsonify({
        "status": "success",
        "count": len(rules),
        "rules": [r.to_dict() for r in rules],
    }), 200
