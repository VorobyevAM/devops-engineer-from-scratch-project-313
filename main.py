import os

import uvicorn

from devops_engineer_from_scratch_project_313.app import create_app

app = create_app()


def run() -> None:
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run()
