"""
Monitoring routes module.

This file contains all the routes required to monitor the API and the model.
"""

import datetime
import threading
from typing import Optional
from flask import Blueprint, Response, jsonify, request, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, \
    generate_latest
from src.app.db_manager import db
from src.app.logger_manager import logger_manager
from src.models.games import Game, get_last_games
from src.utils.rbac_decorator import roles_required
from train import main as run_training
import glob
import os
from sqlalchemy import text

# Defining a Blueprint for the monitoring page routes
monitoring_management = Blueprint("monitoring_management", __name__)

LOSS_RATE_THRESHOLD = 0.75

REQUEST_COUNT = Counter(
    'http_requests_local',
    'Total HTTP Requests',
    ['method', 'endpoint']
)

AI_LAST_10_WIN_RATE = Gauge(
    'ttt_ai_last_10_win_rate',
    'Win rate of the AI in the last 10 saved games'
)
AI_LAST_10_LOSS_RATE = Gauge(
    'ttt_ai_last_10_loss_rate',
    'Loss rate of the AI in the last 10 saved games'
)
AI_LAST_10_DRAW_RATE = Gauge(
    'ttt_ai_last_10_draw_rate',
    'Draw rate of the AI in the last 10 saved games'
)
AI_LAST_10_KNOWN_GAMES = Gauge(
    'ttt_ai_last_10_known_games',
    'Number of last 10 saved games with a determinable AI outcome'
)
AI_LAST_10_SHOULD_RETRAIN = Gauge(
    'ttt_ai_last_10_should_retrain',
    'Indicator whether the AI should retrain based on last 10 saved games',
)


# Global lock to prevent parallel trainings
training_lock = threading.Lock()

# Global variables to store the latest training result message and status
training_result_message = "No training has been run yet."
# Possible values: "idle", "running", "finished", "error"
training_status = "idle"


def update_last_game_metrics() -> None:
    try:
        games = get_last_games(limit=10)
        ai_wins = 0
        ai_losses = 0
        draws = 0
        known_games = 0

        for game in games:
            ai_outcome = _ai_outcome(game)
            if ai_outcome == "win":
                ai_wins += 1
                known_games += 1
            elif ai_outcome == "loss":
                ai_losses += 1
                known_games += 1
            elif ai_outcome == "draw":
                draws += 1
                known_games += 1

        loss_rate = ai_losses / known_games if known_games else 0.0

        AI_LAST_10_WIN_RATE.set(ai_wins / known_games if known_games else 0.0)
        AI_LAST_10_LOSS_RATE.set(loss_rate)
        AI_LAST_10_DRAW_RATE.set(draws / known_games if known_games else 0.0)
        AI_LAST_10_KNOWN_GAMES.set(known_games)
        AI_LAST_10_SHOULD_RETRAIN.set(
            1 if loss_rate >= LOSS_RATE_THRESHOLD else 0
            )
    except Exception as e:
        logger_manager.error(
            f"Error while updating Prometheus metrics: {str(e)}"
            )


@monitoring_management.route("/metrics", methods=["GET"])
def metrics() -> Response:
    """
    Get the metrics scraped by Prometheus.
    ---
    tags:
        - Monitoring
    responses:
        200:
            description: Returns the metrics in text format.
    """
    update_last_game_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def _parse_game_result(game: Game) -> str:
    if not game.game_result:
        return "unknown"

    result = str(game.game_result).strip().lower()
    if result in ("1/2-1/2"):
        return "draw"
    if result == "1-0":
        return "x_wins"
    if result == "0-1":
        return "o_wins"
    if result in ("x", "x wins", "x win", "player x wins", "x victory"):
        return "x_wins"
    if result in ("o", "o wins", "o win", "player o wins", "o victory"):
        return "o_wins"

    if "draw" in result or "tie" in result:
        return "draw"

    return "unknown"


def _detect_ai_side(game: Game) -> Optional[str]:
    if game.id_user_x is None and game.id_user_o is not None:
        return "X"
    if game.id_user_o is None and game.id_user_x is not None:
        return "O"
    return None


def _ai_outcome(game: Game) -> str:
    parsed_result = _parse_game_result(game)
    ai_side = _detect_ai_side(game)

    if parsed_result == "draw":
        return "draw"
    if ai_side is None or parsed_result == "unknown":
        return "unknown"

    if parsed_result == "x_wins":
        return "win" if ai_side == "X" else "loss"
    if parsed_result == "o_wins":
        return "win" if ai_side == "O" else "loss"

    return "unknown"


@monitoring_management.route("/last-game-results", methods=["GET"])
def last_game_results() -> Response:
    """
    Get the last 10 games results.
    ---
    tags:
        - Monitoring
    responses:
        200:
            description: A JSON dictionnary containing the last 10 games' data,
                         a summary of the last 10 games and a success message.
    """
    try:
        games = get_last_games(limit=10)

        recent_games = []
        ai_wins = 0
        ai_losses = 0
        draws = 0
        known_games = 0

        for game in games:
            ai_outcome = _ai_outcome(game)
            if ai_outcome == "win":
                ai_wins += 1
                known_games += 1
            elif ai_outcome == "loss":
                ai_losses += 1
                known_games += 1
            elif ai_outcome == "draw":
                draws += 1
                known_games += 1

            recent_games.append({
                "id_game": str(game.id_game),
                "game_date": game.game_date.isoformat() if game.game_date else None, # noqa
                "game_result": game.game_result,
                "id_user_x": str(game.id_user_x) if game.id_user_x else None,
                "id_user_o": str(game.id_user_o) if game.id_user_o else None,
                "ai_side": _detect_ai_side(game),
                "ai_outcome": ai_outcome
            })

        loss_rate = ai_losses / known_games if known_games else 0.0
        should_retrain = loss_rate >= LOSS_RATE_THRESHOLD

        AI_LAST_10_WIN_RATE.set(ai_wins / known_games if known_games else 0.0)
        AI_LAST_10_LOSS_RATE.set(loss_rate)
        AI_LAST_10_DRAW_RATE.set(draws / known_games if known_games else 0.0)
        AI_LAST_10_KNOWN_GAMES.set(known_games)
        AI_LAST_10_SHOULD_RETRAIN.set(1 if should_retrain else 0)

        return jsonify({
            "last_games": recent_games,
            "summary": {
                "ai_wins": ai_wins,
                "ai_losses": ai_losses,
                "draws": draws,
                "known_games": known_games,
                "loss_rate": loss_rate,
                "should_retrain": should_retrain
            },
            "message": "Last 10 games fetched from the database."
            }), 200
    except Exception as e:
        logger_manager.error(
            f"Error while fetching last game results: {str(e)}"
            )
        raise


@monitoring_management.route("/retrain-model", methods=["POST"])
@roles_required(['Admin'])
def retrain_model() -> Response:
    """
    Starts the asynchronous model retraining, but only if no other training is
    running.
    ---
    tags:
        - Monitoring
    security:
        - Bearer: []
    consumes:
        - application/json
    parameters:
        - in: body
          name: payload
          required: true
          schema:
            type: object
            properties:
                population_size:
                    type: integer
                games_per_eval:
                    type: integer
                mutation_rate:
                    type: float
                mutation_std:
                    type: float
                generations:
                    type: integer
    responses:
        202:
            description: A JSON dictionnary containing a success message.
        409:
            description: Training already in progress.
    """
    global training_result_message, training_status
    data = request.json

    if not data:
        logger_manager.error("No data provided")
        return jsonify(
            message="Error: No data provided"
            ), 400

    if not training_lock.acquire(blocking=False):
        logger_manager.error("Only one training can run at a time")
        return jsonify(
            message="Error: Only one training can run at a time"
            ), 409

    def training_wrapper():
        global training_result_message, training_status
        try:
            training_status = "running"
            result = run_training(
                population_size=data.get("populationSize"),
                games_per_eval=data.get("gamesPerEval"),
                mutation_rate=data.get("mutationRate"),
                mutation_std=data.get("mutationStd"),
                generations=data.get("generations"),
            )
            training_result_message = result or "Training finished, but no message returned." # noqa
            training_status = "finished"
        except Exception as e:
            training_result_message = f"Training failed: {e}"
            training_status = "error"
        finally:
            training_lock.release()
    try:
        threading.Thread(target=training_wrapper, daemon=True).start()
        training_result_message = "Retraining running in the background"
        training_status = "running"
        logger_manager.info("Retraining started in the background")
        return jsonify(message="Retraining started in the background"), 202
    except Exception as e:
        training_lock.release()
        logger_manager.error(f"Error while starting retraining: {str(e)}")
        raise


@monitoring_management.route("/training-result", methods=["GET"])
def get_training_result() -> Response:
    """
    Returns the latest training result message and URLs to the latest plots.
    """
    import os
    # List all PNG files in training_report
    report_dir = os.path.join(os.getcwd(), "training_report")
    plot_files = []
    if os.path.exists(report_dir):
        for f in glob.glob(os.path.join(report_dir, "*.png")):
            plot_files.append(
                f"/api/monitoring/training-report/{os.path.basename(f)}"
                )
    return jsonify({
        "message": training_result_message,
        "plots": plot_files
    })


@monitoring_management.route("/training-status", methods=["GET"])
def get_training_status() -> Response:
    """
    Returns the current training status (idle, running, finished, error).
    """
    return jsonify({"status": training_status})


@monitoring_management.before_request
def count_request() -> Response:
    """
    Counts the number of routes being called from the frontend application.
    Automatically triggered before any request.
    ---
    tags:
        - Monitoring
    """
    REQUEST_COUNT.labels(method='GET', endpoint='/').inc()


@monitoring_management.route("/", methods=["GET"])
def health() -> Response:
    """
    Checks the API health by executing a simple "SELECT" query in the database.
    ---
    tags:
        - Monitoring
    responses:
        202:
            description: A JSON dictionnary containing the API health status
                         and a timestamp of the moment the status was checked.
    """
    try:
        db.session.execute(text("SELECT 1"))
        db.session.commit()
        return {
            "status": "ok",
            "timestamp": datetime.datetime.utcnow()
        }
    except Exception as e:
        logger_manager.error(f"Health check failed: {e}")
        Response.status_code = 503
        return {
            "status": "fail",
            "timestamp": datetime.datetime.utcnow(),
            "error": str(e)
        }


@monitoring_management.route("/training-report/<filename>")
def get_training_report_file(filename):
    """
    Serve a file from the training_report directory.
    """
    report_dir = os.path.join(os.getcwd(), "training_report")
    return send_from_directory(report_dir, filename)
