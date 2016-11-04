#!/usr/bin/python3
# System
import argparse
import sys
import os
import time
import logging
import csv
from logging.handlers import TimedRotatingFileHandler
import json
from pyvirtualdisplay import Display
import selenium.common.exceptions
# Local
import initium
import string
import re

def create_timed_rotating_log(path):
    # Create logger
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    # Create formatter
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")

    # Rotating file handler
    fileHandler = TimedRotatingFileHandler(path, when="midnight", interval=1, backupCount=5)
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    # Console output handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    return logger


class Bot(initium.webdriver, initium.initium):
    def __init__(self):
        self.cfg = self._parse_config()

        logger.info("Initializing webdriver")
        super().__init__()

        logger.info("Connecting to Initium")
        self.login(self.cfg['email'], self.cfg['pw'])

    def _parse_config(self):
        logger.info('Parsing command line arguments')
        self._parser = argparse.ArgumentParser(description="Owl - A Python based bot for Initium - http://playinitium.com")
        self._parser.add_argument("-c", "--config", dest="config_file", default="../cfg.json",
                                  help="Configuration to use (default=../cfg.json)")
        self._parser.add_argument("-d", "--do_chat", dest="do_chat", action="store_true",
                                  help="Handle commands in each rooms local chat")
        self._parser.add_argument('-m', '--map', dest='map_file', default='map.json',
                                  help='Map file to use (default=map.json)')
        self._parser.add_argument('-l', '--headless', help='Run in headless operation mode if HEADLESS=true/True/T')
        self.args = self._parser.parse_args()
        if self.args.headless == 'true' or self.args.headless == 'True' or self.args.headless == 'T' or self.args.headless == 'TRUE':
            display = Display(visible=0, size=(800,600))
            display.start()

        logger.info("Reading config")

        if os.path.isfile(self.args.config_file):
            with open(self.args.config_file, encoding="utf-8") as data_file:
                return json.loads(data_file.read())
        else:
            logger.error("Error: Config: {0} not found".format(self.args.config_file))
            sys.exit(1)


if __name__ == "__main__":
    # Initialize logger
    log_file = "../logs/test.log"
    logger = create_timed_rotating_log(log_file)

    # Initialize bot
    bot = Bot()

    # Test location
    logger.info("Current Location: " + bot.get_location())

    # Test gold
    logger.info("Current Gold: " + bot.get_gold())

    # Test messages
    auths, texts, times = bot.update_messages("Global")
    for each in texts:
        print(each)
