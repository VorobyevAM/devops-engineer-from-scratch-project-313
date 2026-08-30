import os

import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.0,
    )


@app.get("/ping")
def ping() -> str:
    return "pong"


@app.errorhandler(Exception)
def handle_exception(error: Exception):
    if isinstance(error, HTTPException):
        return error

    sentry_sdk.capture_exception(error)
    return {"error": "internal server error"}, 500


def run() -> None:
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    run()
