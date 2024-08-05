import requests
from modal.authProxy import check_windows_proxy_configuration
# from authProxy import check_windows_proxy_configuration

proxy_configured, proxy_server = check_windows_proxy_configuration()

proxy = None

if proxy_configured:
    proxy = "http://" + proxy_server
else:
    proxy = ''

proxie = {
    'http': proxy,
    'https': proxy
}

class BDD_MYSQL:

    def __init__(self, param):
        self.link = f"http://localhost/apijuriste/api/MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDa2r13RqeCZ/{param}"
        # self.link = f"https://auditci.alwaysdata.net/api/team05/{param}"

    def getData(self, filter=''):
        url = f"{self.link}/{filter}"
        
        try:

            response = requests.get(url, proxies=proxie)
            response.raise_for_status()
            data = response.json()

            return data

        except requests.exceptions.RequestException as e:
            return False


    def postData(self, arg):
        url = f"{self.link}"

        try:
            response = requests.post(url, json=arg, proxies=proxie)
            response.raise_for_status()
            data = response.json()

            return data

        except requests.exceptions.RequestException as e:
            return False

    def setData(self, filter, arg):
        url = f"{self.link}{filter}"

        try:
            response = requests.put(url, json=arg, proxies=proxie)
            response.raise_for_status()
            data = response.json()

            return data

        except requests.exceptions.RequestException as e:
            return False

    def deleteData(self, filter):
        url = f"{self.link}{filter}"

        try:
            response = requests.delete(url, proxies=proxie)
            response.raise_for_status()
            data = response.json()

            return data

        except requests.exceptions.RequestException as e:
            return False

# db = BDD_MYSQL('user')
# # for item in db.getData():
# #     print(item['id'])

# print(db.postData(1))