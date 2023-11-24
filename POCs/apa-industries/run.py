import wsgiserver

from app import app

d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
server = wsgiserver.WSGIServer(d, '0.0.0.0', 80)
if __name__ == '__main__':
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
