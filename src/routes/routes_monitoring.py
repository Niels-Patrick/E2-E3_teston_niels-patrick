"""
Monitoring routes module.

This file contains all the routes required to monitor the API and the model.
"""

import datetime

from flask import Blueprint, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from src.app.db_manager import db

# Defining a Blueprint for the monitoring page routes
monitoring_management = Blueprint("monitoring_management", __name__)


REQUEST_COUNT = Counter(
    'http_requests_local',
    'Total HTTP Requests',
    ['method', 'endpoint']
)


@monitoring_management.route("/metrics", methods=["GET"])
def metrics() -> Response:
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@monitoring_management.before_request
def count_request() -> Response:
    REQUEST_COUNT.labels(method='GET', endpoint='/').inc()


@monitoring_management.route("/", methods=["GET"])
def health() -> Response:
    try:
        db.session.execute("SELECT 1")
        db.session.commit()
        return {
            "status": "ok",
            "timestamp": datetime.datetime.utcnow()
        }
    except Exception:
        Response.status_code = 503
        return {
            "status": "fail",
            "timestamp": datetime.datetime.utcnow()
        }
