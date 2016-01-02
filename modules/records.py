#!/usr/bin/python3
import argparse
import sys
import os
import time
import logging
import csv
from logging.handlers import TimedRotatingFileHandler
import json
import math
import selenium.common.exceptions
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


class Records(initium.webdriver, initium.initium):
    def __init__(self):
        self.cfg = self._parse_config()

        logger.info("Initializing webdriver")
        # Hax
        #super().__init__()

        logger.info("Connecting to Initium")
        #self.get("http://www.playinitium.com")

        logger.info("Logging in as {0}".format(self.cfg["uname"]))
        # Enter email
        #login = self.find_element_by_name("email")
        #login.send_keys(self.cfg["email"])

        # Enter pw
        #login = self.find_element_by_name("password")
        #login.send_keys(self.cfg["pw"])

        #for button in self.find_elements_by_class_name(
        #        "main-button"):
        #    if button.text == "Login":
        #        button.click()

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

    def calculate_score_weapon(self, dice, size, chance, mult):
        ## Calculates a weapon's score based on
        ## 4D13, 07.77% chance for 3x damage = (4*13) * 3 * (2^1.0777)
        score = dice + 0.4 * math.pow((dice * size), 1.5) * (mult / 4.0) * math.pow(2.2, (1.0+(chance*3/100.0)))
        return score

    def save_records(self, item_name, item_id, item_score):
        ## Loads the file, then saves the item to it
        ## Saves as: [item_score, item_id]
        # Variables for scope
        item_records = []
        records_file = None
        ## Open the file
        # First check if file exists
        path = "../logs/records/items/"+item_name+".txt"
        if os.path.isfile(path):
            # File exists, load it in
            records_file = open(path, 'r')
            reader = csv.reader(records_file)
            for row in reader:
                item_records.append(row)
            records_file.close()

        ## Determine if the item already exists in records
        for each in item_records:
            if str(each[1]) == str(item_id):
                # ID is found in records already
                logger.info("Item is already in records, no need to save.")
                return

        ## Now open file for writing
        records_file = open(path, 'w')

        ## Now append new item
        if len(item_records) == 0:
            item_records.append([item_score, item_id])
        else:
            done = False
            for each in item_records:
                if item_score > float(each[0]):
                    item_records.insert(item_records.index(each), [item_score, item_id])
                    done = True
                    break
            if not done:
                item_records.append([item_score, item_id])
        ## Now write to the file, overwriting it.
        writer = csv.writer(records_file)
        writer.writerows(item_records)
        ## Finish: close file and log success
        records_file.close()
        logger.info("Successfully saved item")
        return





if __name__ == "__main__":
    main_log_file = "../logs/records/main.log"
    logger = create_timed_rotating_log(main_log_file)

    Bot = Records()
    #logger.info("Current Location: " + Bot.get_location())
    logger.info("Now listening for requests")

    # Debug
    # Now try this
    score = Bot.calculate_score_weapon(2, 8, 10, 4)
    print(score)
    Bot.save_records("longsword", 666777888, score)
    score = Bot.calculate_score_weapon(2, 8, 20, 2)
    print(score)
    Bot.save_records("longsword", 567678789, score)

    while True:

        # Check location tab for "hoot" or " owl" in last message
        hootauth, hootmsg = Owl.update_messages("Location")
        for each in hootmsg[0:4]:
            if "Hoot hoot! I am Owl. PM me to search shops!" not in each:
                if "hoot" in each.lower():
                    Owl.say("Location", "Hoot hoot! I am Owl. PM me to search shops!")
                    logger.info("Completed hoot request!")
                    break
                if " owl" in each.lower():
                    Owl.say("Location", "Hoot hoot! I am Owl. PM me to search shops!")
                    logger.info("Completed hoot request!")
                    break
            else:
                break

        # Rebuild list of messages
        authors, texts = [], []
        while (len(authors) == 0):
            authors, texts = Owl.update_messages("Global")
            if (len(authors[0]) == 0):
                authors, queries = [], []

    logger.error("OUTSIDE WHILE TRUE LOOP!")
