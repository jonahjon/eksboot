import logging
from flask import request

class __RequestFormatter(logging.Formatter):

    def format(self, record):
        # you can set here everything what you need
        # I just added url and id from GET parameter
        record.url = request.url
        record.data = request.data
        return super().format(record)

# format of our log record.
# print url and id of record which was set in format()
__stream_handler = logging.StreamHandler()
__stream_handler.setFormatter(__RequestFormatter(
    '[%(asctime)s %(levelname)s] requested: %(data)s, data: in %(module)s: %(message)s'
))

logger = logging.getLogger('my_loger')
logger.setLevel(logging.INFO)
logger.addHandler(__stream_handler)