import threading, requests, time

class InternetConnection(threading.Thread):
    def __init__(self):
        super(InternetConnection, self).__init__()
        self.__connection = self.__checkConnection()
    @staticmethod
    def __checkConnection():
        try:
            requests.get("http://www.google.com", timeout = 5)
        except (requests.ConnectionError, requests.exceptions.ReadTimeout):
            return False
        return True
    def run(self):
        while True:
            self.__connection = self.__checkConnection()
            time.sleep(1)
    def get(self):
        return self.__connection
