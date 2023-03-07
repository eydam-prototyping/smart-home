from flask import Flask
import logging
from . import air_conditioner_api

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)-10s - %(name)-20s - %(message)s')

app = Flask(__name__)
app.register_blueprint(air_conditioner_api.bp)


if __name__ == "__main__":
    app.run(debug=True)