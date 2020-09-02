# from flask_script import Manager
# from flask_migrate import Migrate, MigrateCommand
#
#
# from __init__ import db,app
#
# migrate = Migrate(app, db)
# manager = Manager(app)
#
# manager.add_command('db', MigrateCommand)
#
#
# if __name__ == '__main__':
#     manager.run()


from ipbedb import app,db

# POSTGRES = {
#     'user': 'vpandey',
#     'pw': 'om16042020',
#     'db': 'pbe_db',
#     'host': 'localhost',
#     'port': '5432',
# }
#
# DATABASE_URI='postgresql+psycopg2         ://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
# app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vpandey:om16042020@localhost:5432/pbe_db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/pbe_db'

from ipbedb.db_model import User,Cluster,Geneanot,Ap2koexp,Ap2komanifest,Ap2time,Ap2timemanifest,Phenodata


db.create_all()
