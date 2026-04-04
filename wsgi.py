"""WSGI entrypoint for production deployments."""

from main import create_app, start_metrics_server


application = create_app()
app = application.flask
socketio = application.socketio
start_metrics_server()
