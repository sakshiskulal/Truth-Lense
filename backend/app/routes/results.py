import os
import uuid
import time
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
import logging
import logging
from werkzeug.utils import secure_filename
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from app.utils.db import get_db
from app.utils.storage import upload_to_cloudinary
from app.utils.file_processing import cleanup_file
from app.models.image_model import analyze_image
from app.models.video_model import analyze_video
from app.models.audio_model import analyze_audio
import jwt


bp = Blueprint("results", __name__)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


def _jwt_secret() -> str:
    return os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "dev-key-deepfake-ai"))


def _get_user_from_auth() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
        return (payload or {}).get("sub")
    except Exception:
        return None


def _infer_media_type(filename: str, mimetype: str | None) -> str:
    name = (filename or "").lower()
    mt = (mimetype or "").lower()
    if any(x in name for x in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]) or mt.startswith("image/"):
        return "image"
    if any(x in name for x in [".mp4", ".mov", ".avi", ".mkv", ".webm"]) or mt.startswith("video/"):
        return "video"
    if any(x in name for x in [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"]) or mt.startswith("audio/"):
        return "audio"
    return "unknown"


@bp.route("/upload", methods=["OPTIONS"])  # explicit preflight handler
def upload_options():
    # Flask-CORS should add headers; return empty 204
    return ("", 204)


@bp.route("/upload", methods=["POST", "OPTIONS"])
def upload_and_analyze():
    if request.method == "OPTIONS":
        # CORS preflight
        return ("", 204)

    logger.info(
        "/api/upload hit: method=%s headers=%s",
        request.method,
        {k: v for k, v in request.headers.items() if k.lower() in {"authorization", "content-type", "origin", "host"}},
    )
    logger.info("/api/upload hit: method=%s headers=%s", request.method, dict(request.headers))
    # Auth
    email = _get_user_from_auth()
    if not email:
        return jsonify({"detail": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"detail": "Missing file"}), 400
    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"detail": "Empty file"}), 400

    filename = secure_filename(file.filename)
    # Save temp file
    temp_path = os.path.join("/tmp", f"tl_{uuid.uuid4().hex}_{filename}")
    try:
        file.save(temp_path)
    except Exception:
        return jsonify({"detail": "Failed to save uploaded file"}), 400

    media_type = _infer_media_type(filename, file.mimetype)
    if media_type == "unknown":
        cleanup_file(temp_path)
        return jsonify({"detail": "Unsupported media type"}), 400

    # Upload to Cloudinary first
    ok, secure_url, public_id = upload_to_cloudinary(temp_path, resource_type="auto")
    if not ok or not secure_url:
        cleanup_file(temp_path)
        return jsonify({"detail": "Failed to upload to storage"}), 502

    # Analyze
    t0 = time.time()
    try:
        if media_type == "image":
            analysis = analyze_image(temp_path)
        elif media_type == "video":
            analysis = analyze_video(temp_path)
        else:
            analysis = analyze_audio(temp_path)
    finally:
        cleanup_file(temp_path)

    # Build result document compatible with frontend
    verdict = "Fake" if analysis.get("isDeepfake") else "Real"
    trust_score = int(round(analysis.get("confidence", 50)))
    result_doc = {
        "user_email": email,
        "file_name": filename,
        "file_type": media_type,
        "file_url": secure_url,
        "storage_id": public_id,
        "analysis": {
            "ai_analysis": {
                "score": analysis.get("confidence", 0) / 100.0,
                "model": analysis.get("modelUsed", "Lightweight")
            },
            "azure_checked": False,
            "news_checked": False,
        },
        "verdict": verdict,
        "trust_score": trust_score,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "processing_time": round(time.time() - t0, 3),
    }
    # Include anomalies if present
    if "anomalies" in analysis:
        result_doc["analysis"]["anomalies"] = analysis["anomalies"]

    try:
        db = get_db()
        res = db.results.insert_one(result_doc)
        rid = str(res.inserted_id)
    except (ServerSelectionTimeoutError, PyMongoError) as e:
        return jsonify({"detail": "Database unavailable", "error": str(e)}), 503

    return jsonify({"result_id": rid}), 201


@bp.route("/results/<rid>", methods=["GET"])
def get_result(rid):
    email = _get_user_from_auth()
    if not email:
        return jsonify({"detail": "Unauthorized"}), 401

    from bson import ObjectId
    try:
        db = get_db()
        doc = db.results.find_one({"_id": ObjectId(rid), "user_email": email})
    except Exception as e:
        return jsonify({"detail": "Not found"}), 404

    if not doc:
        return jsonify({"detail": "Not found"}), 404

    # Shape for frontend Result.jsx
    return jsonify({
        "id": str(doc["_id"]),
        "file_name": doc.get("file_name"),
        "file_type": doc.get("file_type"),
        "file_url": doc.get("file_url"),
        "verdict": doc.get("verdict"),
        "trust_score": doc.get("trust_score"),
        "created_at": doc.get("created_at"),
        "analysis": doc.get("analysis", {}),
    })


@bp.route("/history", methods=["GET"])
def get_history():
    email = _get_user_from_auth()
    if not email:
        return jsonify({"detail": "Unauthorized"}), 401

    try:
        db = get_db()
        cursor = db.results.find({"user_email": email}).sort("_id", -1).limit(100)
        items = []
        for d in cursor:
            items.append({
                "id": str(d["_id"]),
                "file_name": d.get("file_name"),
                "file_type": d.get("file_type"),
                "verdict": d.get("verdict"),
                "trust_score": d.get("trust_score"),
                "created_at": d.get("created_at"),
            })
    except (ServerSelectionTimeoutError, PyMongoError) as e:
        return jsonify({"detail": "Database unavailable", "error": str(e)}), 503

    return jsonify(items)
