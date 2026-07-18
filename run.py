import os

from app import create_app

if __name__ == "__main__":
    app = create_app()
    if os.path.isfile("certs/cert.pem") and os.path.isfile("certs/key.pem"):
        app.run(
            host=app.config["SERVER_HOST_WITH_CERTS"],
            port=app.config["SERVER_PORT_WITH_CERTS"],
            ssl_context=("certs/cert.pem", "certs/key.pem"),
        )
    else:
        app.run(
            host=app.config["SERVER_HOST_NO_CERTS"],
            port=app.config["SERVER_PORT_NO_CERTS"],
        )
