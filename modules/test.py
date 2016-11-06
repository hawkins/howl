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
        self._parser = argparse.ArgumentParser(description="A Python based bot for Initium - http://playinitium.com")
        self._parser.add_argument("-c", "--config", dest="config_file", default="../cfg.json",
                                  help="Configuration to use (default=../cfg.json)")
        self._parser.add_argument('-l', '--headless', action="store_true",
                                  help='Run in headless operation mode')
        self.args = self._parser.parse_args()
        if self.args.headless:
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

    # # Test location
    # logger.info("Current Location: " + bot.get_location())

    # # Test gold
    # logger.info("Current Gold: " + bot.get_gold())

    # # Test say
    # logger.info("Saying \'Hello from Howl 2.0!\' in local chat")
    # bot.say('Hello from Howl 2.0!', 'Location')

    # # Test messages
    # logger.info('Loading Global chat messages...')
    # messages = bot.get_chat_messages('Global')
    # print('%s %s: %s' % (messages[0]['time'], messages[0]['author'], messages[0]['text']))

    # # Test reply
    # logger.info('Replying in private chat to [Dev] Rade')
    # bot.reply('Testing private message', '[Dev] Rade')

    # # Test getting item stats via inventory
    # bot.send_keypresses('i')
    # while True:
    #     try:
    #         e = bot.find_element_by_xpath("//div[@class='main-item-container']//a[1]")
    #         print(bot.get_item_stats(e))
    #         # e.click()
    #     except selenium.common.exceptions.NoSuchElementException as e:
    #         print("Uh oh")
    #         print(e)
    #         time.sleep(1)

    # Exit the webdriver
    logger.info('Closing webdriver')
    bot.quit()
