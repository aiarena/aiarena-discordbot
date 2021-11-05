import logging


class APIException(Exception):
    def __init__(self, message, request, response):
        self.message = message
        self.request = request
        self.response = response
        logging.error(f"{self.request} returned status code: {self.response.status_code}")

    def __str__(self):
        return self.message
