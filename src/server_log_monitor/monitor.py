import os
import sys
import time
import logging

logging.basicConfig(filename="monitor.log", level=logging.DEBUG)


def monitor_server_log():
    """
    Watch the /home/pi/src/server/log/server.log file.
    Once the file hits 50 MB, dump the contents
    """

    logging.info("monitor_server_log() init...")

    # path = "/Users/reidich/dev/ferring-idweek-server/src/server/log/server.log"
    path = "/home/pi/src/server/log/server.log"

    # Main loop to keep checkoing log
    while True:

        try:

            # try to get the log filesize
            f = os.path.getsize(path)

        except Exception as e:

            logging.error(
                "monitor_server_log(): Unnable to get filesize: \n{}".format(e))

        # if the log is over 50MB, empy he log contents
        if f > 5e+7:

            try:

                logging.info(
                    "monitor_server_log(): Log file over 50MB, emptying log\nfilesize: {}".format(f))
                # opens the file in python,
                # then overwrites all content with nothing
                open(path, 'w').close()

            except Exception as e:

                logging.error(
                    "monitor_server_log(): Unnable to clear log file: \n{}".format(e))

        time.sleep(2)


monitor_server_log()
