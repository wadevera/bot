import requests

# Prueba de conexión a la API de Gate.io
gateio_url = 'https://api.gateio.ws/api2/1/tickers'
try:
    response = requests.get(gateio_url)
    response.raise_for_status()  # Verificar si la respuesta tiene algún error
    print('Conexión exitosa a la API de Gate.io')
except requests.exceptions.RequestException as e:
    print('Error al conectarse a la API de Gate.io:', e)

# Prueba de conexión a otro dominio público (por ejemplo, Google)
google_url = 'https://www.google.com'
try:
    response = requests.get(google_url)
    response.raise_for_status()  # Verificar si la respuesta tiene algún error
    print('Conexión exitosa a', google_url)
except requests.exceptions.RequestException as e:
    print('Error al conectarse a', google_url, ':', e)
