import requests
import hashlib
import hmac

def getSign(params, secretKey):
    sign = ''
    for key in params.keys():
        value = str(params[key])
        sign += key + '=' + value + '&'
    sign = sign[:-1]

    mySign = hmac.new(secretKey.encode(), sign.encode(), hashlib.sha512).hexdigest()
    return mySign

def httpGet(url, resource, params=''):
    full_url = 'https://' + url + '/' + resource + '/' + params
    response = requests.get(full_url)
    return response.json()


""" def httpGet(url, resource, params=''):
    full_url = f"{url}/{resource}/{params}"
    response = requests.get(full_url)
    data = response.json()
    return data """

def httpPost(url, resource, params, apiKey, secretKey):
    full_url = f"https://{url}{resource}"
#    full_url = 'https://' + url + '/' + resource
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "KEY": apiKey,
        "SIGN": getSign(params, secretKey)
    }
    print("full url: " + full_url)
    response = requests.post(full_url, data=params, headers=headers)
    print(response)
    data = response.json()
    params.clear()
    return data


""" def httpPost(url, resource, params, apiKey, secretKey):
    full_url = f"{url}/{resource}"
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "KEY": apiKey,
        "SIGN": getSign(params, secretKey)
    }
    response = requests.post(full_url, data=params, headers=headers)
    data = response.json()
    params.clear()
    return data """
