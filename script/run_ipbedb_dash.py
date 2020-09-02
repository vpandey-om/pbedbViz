from ipbedb import dashapp1 as app1
from ipbedb import app as flask_app
# from ipbedb import server as server
from werkzeug.serving import run_simple

from werkzeug.middleware.dispatcher import DispatcherMiddleware

application = DispatcherMiddleware(flask_app, {
    '/gene': app1.server,
})

if __name__ == '__main__':
    run_simple('localhost', 8050, application)


# if __name__ == '__main__':
#     # app.run_server(debug=True)
