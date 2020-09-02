import os,pickle
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

import dash




def simple(env, resp):
    resp(b'200 OK', [(b'Content-Type', b'text/plain')])
    return [b'Hello WSGI World']




class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]


app = Flask(__name__)
app.config['SECRET_KEY']='ee4f27a8c95880dcf3e45fc59320af39'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

cur_dir = os.path.dirname(__file__)
malaria_atlas_list= pickle.load(open(os.path.join(cur_dir,'external', 'malaria_cell_atlas.pickle'), 'rb'))


# print (genes)
###

POSTGRES = {
    'user': 'vpandey',
    'pw': 'om16042020',
    'db': 'pbe_db',
    'host': 'localhost',
    'port': '5432',
}

DATABASE_URI='postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vpandey:om16042020@localhost:5432/pbe_db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/pbe_db'
# app.config['APPLICATION_ROOT'] = '/pbedb'
# app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/pbedb')
# app.wsgi_app = DispatcherMiddleware(simple, {'/pbedb': app.wsgi_app})


db = SQLAlchemy(app)
db.create_all()
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'

from ipbedb import routes


from ipbedb.dashapp1.app import dashapp1
from ipbedb.dashapp1.app import register_callbacks

register_callbacks(dashapp1)
