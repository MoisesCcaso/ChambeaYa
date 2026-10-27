import os

from frameworks.flask_mvc.app import create_app

app = create_app()


def main():
    """punto de entrada ejecutable 'chambeaya' generado por Poetry."""
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
    )


if __name__ == "__main__":
    app.run()
