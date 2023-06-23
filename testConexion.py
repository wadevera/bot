import socket

def test_outgoing_connection(host, port):
    try:
        sock = socket.create_connection((host, port), timeout=5)
        sock.close()
        return True
    except Exception as e:
        print(f"Error al conectar a {host}:{port}")
        print(str(e))
        return False

# Prueba de conexión a la URL 'https://api.gateio.ws/api2/1/tickers'
url_host = "api.gateio.ws"
url_port = 443
if test_outgoing_connection(url_host, url_port):
    print("Conexión saliente exitosa a", url_host)
else:
    print("No se pudo establecer la conexión saliente a", url_host)
