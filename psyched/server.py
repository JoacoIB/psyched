"""This module exports the serve_dag function."""
import os
import pathlib

from flask import Flask, jsonify


app = Flask(
    __name__,
    static_url_path=os.path.join(
        pathlib.Path(__file__).parent.absolute(),
        'static'
        )
    )


def serve_dag(dag):
    """Present a dag on the psyched http server.

    :param dag: dag to serve
    :type dag: DAG
    """
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/dag')
    def dag_status():
        result = [
            {
                'name': task.name,
                'status': task.status,
                'upstream': [t.name for t in task.get_upstream()],
                'downstream': [t.name for t in task.get_downstream()],
            }
            for task in dag.tasks.values()
        ]
        return jsonify(result)
    app.run()
