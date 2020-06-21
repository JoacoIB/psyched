"""This module exports the serve_dag function."""
import os
import pathlib

from flask import Flask

app = Flask(
    __name__,
    static_url_path=os.path.join(
        pathlib.Path(__file__).parent.absolute(),
        'static'
        )
    )


def _build_api(dag):
    @app.route('/')
    def index():
        return app.send_static_file('index.html')


def serve_dag(dag):
    """Present a dag on the psyched http server.

    :param dag: dag to serve
    :type dag: DAG
    """
    _build_api(dag)
    app.run()
