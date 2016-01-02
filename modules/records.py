#!/usr/bin/python3
import argparse
import sys
import os
import time
from timeout import timeout
import logging
from pyvirtualdisplay import Display
import csv
from logging.handlers import TimedRotatingFileHandler
import json
import math
from selenium.common.exceptions import *
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
        super().__init__()

        logger.info("Connecting to Initium")
        self.get("http://www.playinitium.com")

        logger.info("Logging in as {0}".format(self.cfg["uname"]))
        # Enter email
        login = self.find_element_by_name("email")
        login.send_keys(self.cfg["email"])

        # Enter pw
        login = self.find_element_by_name("password")
        login.send_keys(self.cfg["pw"])

        for button in self.find_elements_by_class_name(
               "main-button"):
           if button.text == "Login":
               button.click()

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

    # @timeout(60)
    def calculate_score_weapon(self=0, dice=0, sides=0, chance=0, mult=0):
        ## Calculates a weapon's score based on damaeg and critical stats
        # Ensure the popup loads but we don't wait too long
        start = time.time()
        DEF_MAX_RUNTIME = 14.9
        loaded = False
        while not loaded:
            try:
                end = time.time()
                if end-start > DEF_MAX_RUNTIME:
                    logger.warning("Score calculation timed out!")
                    return -1
                elements = self.find_elements_by_class_name("main-item-subnote")
                damage = elements[0].get_attribute("innerHTML").split("D")
                try:
                    dice = int(damage[0])
                except ValueError:
                    logger.warning("Inspected armor item!")
                    return -1
                sides = int(damage[1])
                chance = float(elements[1].get_attribute("innerHTML").split("%")[0])
                mult = float(elements[2].get_attribute("innerHTML").split("x")[0])
                loaded = True
            except:
                pass
        score = dice + 0.4 * math.pow((dice * sides), 1.5) * (mult / 4.0) * math.pow(2.2, (1.0+(chance*3/100.0)))
        return score

    def save_records(self, item_name, item_id, item_score):
        ## Loads the file, then saves the item to it
        ## Saves as: [item_score, item_id]
        # Variables for scope
        item_records = []
        records_file = None
        result = -1
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
                return result

        ## Now open file for writing
        records_file = open(path, 'w')

        ## Now append new item
        if len(item_records) == 0:
            item_records.append([item_score, item_id])
            result = 0
        else:
            done = False
            for each in item_records:
                if item_score > float(each[0]):
                    result = item_records.index(each) # Where we place the item info
                    item_records.insert(result, [item_score, item_id])
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
        return result





if __name__ == "__main__":
    main_log_file = "../logs/records/main.log"
    logger = create_timed_rotating_log(main_log_file)

    Bot = Records()
    logger.info("Now listening for item shares")

    while True:
        ## Look in Global chat
        Bot.update_messages("Global")

        ## Check for item shares
        items = Bot.find_elements_by_class_name("chat-embedded-item")
        # Iterate through each, saving them all
        for each in items:
            try:
                # Click the item
                link = each.find_elements_by_tag_name("a")[0]
                # for some reason, sometimes this winds up being a share button.
                # so for now, DO NOT CLICK if it says share
                if link.get_attribute("innerHTML") != "Share":
                    link.click()
            except ElementNotVisibleException:
                logger.warning("Item not visible, updating messages instead.")
                break

            # Calculate score of popup item
            score = Bot.calculate_score_weapon()
            if score == -1:
                # Inspecetd item was not a weapon, so skip to next item
                continue
            # Get item ID from "rel="viewitemmini.jsp?itemId=4961250779856896"
            itemID = link.get_attribute("rel").split("itemId=")[1]
            # Get the item name
            original_item_name = ' '.join(link.find_elements_by_tag_name("div")[1].get_attribute("innerHTML").split())
            item_name = ''.join(link.find_elements_by_tag_name("div")[1].get_attribute("innerHTML").split())
            item_name = re.sub('(?!\s)[\W_]', '', item_name) # Need to also strip spaces
            # Save the item
            result = Bot.save_records(item_name, itemID, score)
            if result != -1:
                logger.info("Saved " + original_item_name + " in resulting index " +str(result))
            if result == 0:
                # Best of its kind
                author_element = link.find_elements_by_xpath('../../..')[0].find_elements_by_tag_name("span")[1].find_elements_by_tag_name("a")[0]
                author = author_element.get_attribute("innerHTML")
                Bot.say("Global", author+" has just discovered the best "+original_item_name+", with a score of "+"{:10.2f}".format(score) + "!" )

    logger.error("OUTSIDE WHILE TRUE LOOP!")
