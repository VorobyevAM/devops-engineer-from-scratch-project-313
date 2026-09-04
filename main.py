import os

import uvicorn

from hexlet_code.app import create_app

app = create_app()


def run() -> None:
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run()
