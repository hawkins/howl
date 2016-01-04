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
        self._parser = argparse.ArgumentParser(description="Bower - A Python based bot for Initium - http://playinitium.com")
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
        time.sleep(1)
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
                #logger.warning("Ignoring non-equipment item.") # Score remains -1
                pass
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

    def load_records(self, file_path):
        ## Loads records from a file and returns a 2 dimensional array of all records in the file
        ## Define Variables
        item_records = []
        ## Open the file
        # First check if file exists
        if os.path.isfile(file_path):
            # File exists, load it in
            records_file = open(file_path, 'r')
            reader = csv.reader(records_file)
            for row in reader:
                item_records.append(row)
            records_file.close()
        ## Now return the array
        return item_records

    def remove_record(self, file_path, rank):
        ## Deletes an individual item by rank from the records file
        ## Note Rank is 1-infinity where 1 is the best. -1 represents ALL records
        # Load the records
        records = self.load_records(file_path)
        if rank == -1:
            ## Delete ALL records
            # Simply delete the file
            try:
                os.remove(file_path)
                logger.info("Successfully removed all entries of the item.")
                return
            except:
                logger.error("An error occurred while deleting the file: " + file_path)
        else:
            # Delete the item
            del records[rank-1]
            ## Save new records
            # Open file for writing
            records_file = open(file_path, 'w')
            # Now write to the file, overwriting it.
            writer = csv.writer(records_file)
            writer.writerows(records)
            # Close the file
            records_file.close()
            logger.info("Successfully removed item.")
            return
        self.say("Global", "Successfully removed the item(s).")

    def save_records(self, item_name, item_id, item_score):
        ## Loads the file, then saves the item to it
        ## Saves as: [item_score, item_id]
        # Variables for scope
        item_records = []
        records_file = None
        result = -1
        ## Load records from file path
        path = "../logs/records/items/"+item_name+".txt"
        item_records = self.load_records(path)

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
    # Create a logger for all functions to use
    main_log_file = "../logs/records/main.log"
    logger = create_timed_rotating_log(main_log_file)

    # Create the bot, which begins login process
    Bot = Records()

    ## We will ignore the DEF_MAX_RECENT_REQUESTS # of recent requests
    ## In other words, if a lookup request was one of the DEF_MAX_RECENT_REQUESTS most recent requests, we will ignore it
    # First define variables
    recent_lookup_requests = []
    DEF_MAX_RECENT_REQUESTS = 6
    ## Now let's repopulate the recent requests incase we crash after answering a request
    reqauth, reqmsg = Bot.update_messages("Global")
    for each in reqmsg:
        #print("Author: " + reqauth[reqmsg.index(each)] + ". Msg: " + each)
        if "#" in each and "[Bot] Bower" == reqauth[reqmsg.index(each)]:
            ## If we sent a request here, append the item to the recent list
            # Identify the item
            item = each.split(" ", 2)[2]
            item = item.split(" with a score")[0]
            # Append it if we haven't already
            if item not in recent_lookup_requests:
                recent_lookup_requests.append(item)
    # If recent_lookup_requests is too large, resize it
    while len(recent_lookup_requests) > DEF_MAX_RECENT_REQUESTS:
        recent_lookup_requests = recent_lookup_requests[1:DEF_MAX_RECENT_REQUESTS]
    # Inform administrator of recent lookups
    logger.warning("Assuming recent lookups of: " + str(recent_lookup_requests))

    # Make sure we don't accidentally repeat admin commands
    last_admin_command = None
    # See if we have a recent admin command
    for each in reqmsg[0:30]:
        if "bower rm" in each:
            last_admin_command = each
            break
    logger.warning("Assuming last admin command of: " + str(last_admin_command))

    # Tell logger we're ready to operate
    logger.info("Now listening for item shares")

    while True:
        ## Look in Global chat
        Bot.update_messages("Global")

        ## Check for item shares
        items = Bot.find_elements_by_class_name("chat-embedded-item")
        # Iterate through each, saving them all
        for each in items:
            score = 0
            try:
                # Click the item
                link = each.find_elements_by_tag_name("a")[0]
                # for some reason, sometimes this winds up being a share button.
                # so for now, DO NOT CLICK if it says share
                if link.get_attribute("innerHTML") != "Share":
                    link.click()
                    #print(str(Bot.get_item_stats()))
            except ElementNotVisibleException as e:
                #logger.error(str(e))
                #logger.warning("Item not visible, checking for lookup requests instead.")
                break
            except StaleElementReferenceException as e:
                logger.error(str(e))
                logger.error("StaleElementReferenceException occurred! ! ! !")
                logger.error("Checking for lookup requests instead.")
                break

            # Calculate score of popup item
            score = Bot.score_item()
            if float(score) <= 2.0 or float(score) >= 400.0: # 1.64 default, 400 never been seen
                # Inspeceed item was not a scorable item, so skip to next item
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
                logger.info("Found #" + str(result+1) + " "+ original_item_name + ". Score: " + str(score))
            author_element = link.find_elements_by_xpath('../../..')[0].find_elements_by_tag_name("span")[1].find_elements_by_tag_name("a")[0]
            if result == 0:
                ## Best of its kind
                # Get author name
                author = author_element.get_attribute("innerHTML")
                # Announce in global chat and private message
                Bot.say("Global", author+" discovered the best Item("+itemID+"), with a score of "+"{:10.2f}".format(score) + "!" )
                time.sleep(1) # Avoiding chat ban
                Bot.reply(author_element, "Your Item(" + itemID + ") is the BEST so far!! Score: " + "{:10.2f}".format(score) + "!" )
            else:
                if result > 0:
                    # Whisper author
                    Bot.reply(author_element, "Your Item(" + itemID + ") is the #" + str(result+1) + "in the game! Score: " + "{:10.2f}".format(score) + "!" )

        ## Listen for requests in Global chat
        ## "Bower Longsword" or "Bower The Black Blade"
        authors, messages = Bot.update_messages("Global")
        for each in messages[:14]:
            if "bower " in each.lower():
                ## Did Rade ask us?
                # NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE
                # NOTE: SLACK SUPPORT VULNERABILITY HERE! NOTE
                # NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE NOTE
                if "rade" in authors[messages.index(each)].lower() or "rade: bower rm " in each:
                    # If this command is new,
                    if each != last_admin_command:
                        # Then make sure we don't run it again
                        last_admin_command = each
                        if " rm " in each:
                            logger.info("Received remove request from Rade")
                            # Get the item name and file name
                            goal = each.split("rm ")[1]
                            goal = goal.split(" ")
                            rank = goal[len(goal)-1]
                            goal = goal[0:len(goal)-1] # Chop off rank
                            file_goal = ''.join(goal)
                            file_goal = re.sub('(?!\s)[\W_]', '', file_goal)
                            ## Now remove the file
                            if "all" == rank:
                                # Remove ALL values form the file
                                Bot.remove_record("../logs/records/items/"+file_goal+".txt", -1)
                            else:
                                # Remove specified values from the file
                                Bot.remove_record("../logs/records/items/"+file_goal+".txt", int(rank))
                            # Restart the bot
                            sys.exit(0)

                logger.info("Processing lookup request...")
                goal = None
                try:
                    goal = each.split("ower ")[1] # Everything after bower
                    file_goal = ''.join(goal.split())
                    file_goal = re.sub('(?!\s)[\W_]', '', file_goal)
                    if goal in recent_lookup_requests:
                        # Ignore the request
                        logger.warning("Ignoring recent request!")
                        continue
                    logger.info("Received lookup request for \"" + goal + "\" in file \"" + file_goal + ".txt\"")
                except e:
                    logger.error("An error occurred while procesing lookup request")
                    logger.error(e)
                    continue
                item_records = Bot.load_records("../logs/records/items/"+file_goal+".txt")
                # Mention first 3 in global
                try:
                    Bot.say("Global", "#1 Item(" + item_records[0][1] + ") with a score of " + "{:10.2f}".format(float(item_records[0][0])) + "!!!")
                    time.sleep(1)
                    Bot.say("Global", "#2 Item(" + item_records[1][1] + ") with a score of " + "{:10.2f}".format(float(item_records[1][0])) + "!!")
                    time.sleep(1)
                    Bot.say("Global", "#3 Item(" + item_records[2][1] + ") with a score of " + "{:10.2f}".format(float(item_records[2][0])) + "!")
                except IndexError as e:
                    logger.warning("An error occurred processing top 3 of " + goal)
                    logger.error(e)

                # Add the goal to recent_lookup_requests so we don't spam it.
                recent_lookup_requests.append(goal)

                # Take a break before continuing, chat ban avoiding.
                time.sleep(1)

        #If recent_lookup_requests is too large, cut out the first one
        if len(recent_lookup_requests) > DEF_MAX_RECENT_REQUESTS:
            recent_lookup_requests = recent_lookup_requests[1:DEF_MAX_RECENT_REQUESTS]



    logger.error("OUTSIDE WHILE TRUE LOOP!")
