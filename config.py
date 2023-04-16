import connexion
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import pathlib


basedir = pathlib.Path(__file__).parent.resolve()
connex_app = connexion.App(__name__,specification_dir=basedir)

app = connex_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{basedir / 'sensors.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
