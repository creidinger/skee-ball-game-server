import json
import logging
import csv
import logging


def clean_json_data(data):
    """
    Clean up json data coming form game because it is
    occationally grouped together in an improper format
    """

    # Look for <EOF> at the end of the string
    # we need to look for this because the client doesn't always send a full string
    if data[-5:] != "<EOF>":

        logging.info(
            "server_functions.clean_json_data(): partial String received...\n<EOF> not found at end of message. Forcing 'DataRequest' so client can update.\nData Received from client: {}\n".format(data))
        # return "DataRequest" so the client still receives game updates
        return "DataRequest"

    else:
        # logging.info("clean_json_data(): Cleaning...")
        data_array = data.split('<EOF>')
        # logging.info(data_array)
        data = data_array[len(data_array) - 2]
        return data
