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

    def score_item(self):
        ## Score any item by determining its type and calling appropriate functions
        # Sleep for a time to ensure page has updated with new item info
        time.sleep(2)
        # Define Variables
        score = -1
        ## First determine what type of item it is
        # Check <p> tag in popup
        paragraph_element = self.find_elements_by_xpath('//div[contains(@class,"cluetip-inner") and contains(@class, "ui-widget-content") and contains(@class, "ui-cluetip-content")]/div[@class="main-page"]/p')[0]
        #paragraph_element = paragraph_element.find_elements_by_class_name("main-page")[0].find_elements_by_tag_name("p")[0]
        paragraph_text = paragraph_element.get_attribute("innerHTML").lower()
        # Weapon or Armor?
        if "weapon" in paragraph_text:
            score = self.calculate_score_weapon()
        else:
            if "armor" in paragraph_text:
                if "shirt" in paragraph_text:
                    score = self.calculate_score_armor(shirt=True)
                else:
                    score = self.calculate_score_armor(shirt=False)
            else:
                # Not weapon or armor so we don't score it!
                logger.warning("Ignoring non-equipment item.") # Score remains -1
        return score

    def calculate_score_armor(self, chance=0, reduction=0, penalty=0, shirt=False):
        ## Calculates an armor's score based on block chance, damage reduction, and dexterity penalty
        ## Note this calculation varies if a shirt is tested
        start = time.time()
        DEF_MAX_RUNTIME = 14.9
        loaded = False
        while not loaded:
            try:
                # Check if we've run for too long
                end = time.time()
                if end-start > DEF_MAX_RUNTIME:
                    logger.warning("Score calculation timed out!")
                    return -1
                # Build stat list
                elements = self.find_elements_by_class_name("main-item-subnote")
                chance = int(elements[0].get_attribute("innerHTML").split("%")[0])
                reduction = int(elements[1].get_attribute("innerHTML"))
                penalty = int(elements[2].get_attribute("innerHTML").split("%")[0])
                loaded = True
            except e:
                logger.error(e)
                return -1
        ## Actual calculation
        # Is the item a shirt?
        if shirt:
            score = 1.7 * ((chance / (penalty + 1.0))) * (reduction / 13.33)
        else:
            # Must be normal armor then
            score = chance * (reduction / 25) - penalty # probably should be more complex
        return score

    # @timeout(60)
    def calculate_score_weapon(self, dice=0, sides=0, chance=0, mult=0):
        ## Calculates a weapon's score based on damage and critical stats
        # Ensure the popup loads but we don't wait too long
        start = time.time()
        DEF_MAX_RUNTIME = 14.9
        loaded = False
        while not loaded:
            try:
                # Check if we've run for too long
                end = time.time()
                if end-start > DEF_MAX_RUNTIME:
                    logger.warning("Score calculation timed out!")
                    return -1
                # Build stat list
                elements = self.find_elements_by_class_name("main-item-subnote")
                damage = elements[0].get_attribute("innerHTML").split("D")
                # Is this actually a block chance stat and thus armor piece?
                if "%" in damage:
                    logger.warning("Inspected armor as weapon!")
                    return self.calculate_score_armor() # Call armor instead
                try:
                    dice = int(damage[0])
                except ValueError:
                    #logger.warning("Inspected armor item!")
                    return -1
                # Looks like a weapon, go on
                sides = int(damage[1])
                chance = float(elements[1].get_attribute("innerHTML").split("%")[0])
                mult = float(elements[2].get_attribute("innerHTML").split("x")[0])
                loaded = True
            except:
                pass
        # Actual calculation
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
    # Solve for default score in case of bugs
    #DEF_LOWEST_SCORE = Bot.calculate_score_weapon(0, 0, 0, 0, 0, 0)
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
            except ElementNotVisibleException as e:
                #logger.error(str(e))
                logger.warning("Item not visible, updating messages instead.")
                break
            except StaleElementReferenceException as e:
                logger.error(str(e))
                logger.error("StaleElementReferenceException occurred! ! ! !")
                logger.error("Updating messages instead...")
                break

            # Calculate score of popup item
            score = Bot.score_item()
            if float(score) <= 2.0 or float(score) >= 300.0: # 1.64 default, 300 never been seen
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
                logger.info("Found #" + str(result+1) + " "+ original_item_name + "score: " + str(score))
            author_element = link.find_elements_by_xpath('../../..')[0].find_elements_by_tag_name("span")[1].find_elements_by_tag_name("a")[0]
            if result == 0:
                ## Best of its kind
                # Get author name
                author = author_element.get_attribute("innerHTML")
                # Announce in global chat and private message
                Bot.say("Global", author+" discovered the best Item("+itemID+"), with a score of "+"{:10.2f}".format(score) + "!" )
                time.sleep(0.5) # Avoiding chat ban
                Bot.reply(author_element, "Your Item(" + itemID + ") is the BEST so far!! Score: " + "{:10.2f}".format(score) + "!" )
            if result == 1:
                # Whisper author
                Bot.reply(author_element, "Your Item(" + itemID + ") is the 2nd best! Score: " + "{:10.2f}".format(score) + "!" )
            if result == 2:
                # Whisper author
                Bot.reply(author_element, "Your Item(" + itemID + ") is the 3rd best! Score: " + "{:10.2f}".format(score) + "!" )

        ## Listen for requests in Global chat
        ## "Best itemnamegoeshere" or "#1 itemnamegoeshere" or "#2 itemnamegoeshere" or "#3 itemnamegoeshere"
        #authors, messages = Bot.update_messages("Global")
        #for each in messages[:15]:
            # If string matches regex pattern for #1 or best
            # #2
            # #3



    logger.error("OUTSIDE WHILE TRUE LOOP!")
