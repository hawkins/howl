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


class Owl_Bot(initium.webdriver, initium.initium):
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
    log_file = "../logs/owl.log"
    logger = create_timed_rotating_log(log_file)

    # Create the bot
    Owl = Owl_Bot()
    DEF_MAX_RESULTS = 5
    wanted = -1 # How many results client wanted
    stats = None # Desired stats (weapon attack 0d0/0d00)

    logger.info("Current Location: " + Owl.get_location())

    # Download messages
    messages = Owl.get_chat_messages("Private")
    if messages:
        read = messages[0] # save latest message as read for base case
    else:
        read = None
    logger.info("Marking \"" + str(read) + "\" as read")
    logger.info("Now listening for requests")

    # Run continuously
    while True:
        # Reset success tag for user interaction
        success = False
        # Reset counter flag
        result_counter = 0
        wanted = 0
        stats = None

        # Check location tab for "hoot" or " owl" in last message
        hoot_messages = Owl.get_chat_messages("Location")
        for each in hoot_messages[0:4]:
            if '[Bot] Owl' not in each['author']:
                if 'hoot' in each['text'].lower():
                    Owl.say('Hoot hoot! I am Owl. PM me to search shops!', "Location")
                    logger.info("Completed hoot request!")
                    break
            else:
                break

        # Rebuild list of PMs
        messages = []
        while not messages:
            messages = Owl.get_chat_messages("Private")

        # If latest message has not been processed
        if (messages[0] != read) and (messages[0]['author'] != '[Bot] Owl'):
            q = messages[0]['text']
            print('Query: %s' % q)
            logger.info("Query received from " + messages[0]['author'] + ": " + q)

            # Get a WebElement of the player who requested us
            client = Owl.find_elements_by_xpath('//a[@class="chatMessage-private-nickname"]')[0]
            client_name = client.text

            if "find" in q.lower():
                # Identify the item
                goal = ' '.join(q.split("ind ", 1)[1].split()).lower()

                # Check if client specified how many he wants
                if "find all" in q.lower():
                    wanted = -1 # Will never fire the check statement
                    goal = " ".join(goal.split(" ")[1:])
                    logger.info("-Client specified wanting ALL results")
                else:
                    if goal[0].isdigit():
                        try:
                            wanted = int(goal.split(" ")[0])
                            logger.info("-Client specified wanting " + str(wanted) + " results")
                        except:
                            # Found the damage modifier, so client didn't specify quantity wanted.
                            wanted = DEF_MAX_RESULTS
                            logger.warning("-Assuming client wanted " + str(wanted) + " results")
                        goal = goal.split(" ")[1:]
                    else:
                        wanted = DEF_MAX_RESULTS
                        logger.warning("-Assuming client wanted " + str(wanted) + " results")

                ## Did they specify weapon attack?
                if not isinstance(goal, str):
                    goal = " ".join(goal)
                wep_pat = re.compile("[0-9]d[0-9]+")
                if re.search(wep_pat, goal):
                    stats = re.search(wep_pat, goal).group()
                    goal = re.sub(wep_pat, '', goal).strip()
                    logger.info("-Client specified wanting " + stats + " items")

                # Filter out punctuation
                # Note full-plate because fullplate NOT full plate
                goal = re.sub('(?!\s)[\W_]', '', goal)

                # Ensure goal is not blank ('the Ravager fault')
                if not goal:
                    logger.warning("-Client requested null goal")
                    Owl.reply("Sorry, I don't understand. Did you forget a space?", client_name)
                    continue

                logger.info("- Looking for: %s" % goal)

                # Say "I'll get right on that!"
                Owl.reply("I'll get right on that!", client_name)

                # Click on merchant box
                Owl.find_element_by_xpath('//div[@id="main-merchantlist"]/div').click()

                # Gather list of all shops
                time.sleep(3)
                merchant_elements = Owl.find_elements_by_xpath('//div[@class="main-merchant-container"]/div[@class="main-item"]/a')
                merchants = []
                for element in merchant_elements:
                    merchants.append(element.get_attribute('onclick'))

                # Iterate through each previously made link
                for each in merchants:
                    try:
                        logger.info("-- Checking Merchant ID: " + each)
                        Owl.execute_script(each)
                    except Exception as e:
                        print(e)
                        logger.error("--- An error occurred while loading the merchant.")

                    # Now that store is open, search for the item
                    goal_id = [] # ItemID for goal items (for preview)
                    goal_buy = [] # buy now links to goal items
                    goal_price = [] # prices for the goal item

                    # TODO: Wait until items loaded
                    time.sleep(3)
                    print('store loaded')

                    for i in Owl.find_elements_by_xpath('//div[@class="saleItem"]//div[@class="main-item"]'):
                        # TODO: Remove this print statements
                        print('in item for loop')
                        print(i.text)
                        # Skip sold items
                        try:
                            sold_text = i.find_element_by_class_name('saleItem-sold').text
                            if sold_text:
                                print(sold_text)
                                continue
                        except:
                            pass

                        # Get code to buy item
                        try:
                            buy_code = i.find_elements_by_tag_name('a')[1].get_attribute('onclick')
                        except IndexError as e:
                            print("OOPS! Accidentally inspected a sold item")
                            continue
                        print("Inspecting buy_code: %s" % buy_code)

                        # Get item details
                        print('buy_code: %s' % buy_code)
                        # item_re_match = re.match(r'storeBuyItemNew\((.*), (.*), (.*), (.*), (.*), (.*)\)', buy_code)
                        # if item_re_match:
                        item_name  = buy_code.split(',', 1)[1].rsplit(',', 4)[0]
                        item_price = buy_code.split(',', 2)[2].rsplit(',', 3)[0]
                        item_id    = buy_code.split(',', 3)[3].rsplit(',', 2)[0]
                        print("Item name:  %s" % item_name)
                        print("Item price: %s" % item_price)
                        print("Item ID:    %s" % item_id)

                        # If we found our goal item
                        if goal in item_name:
                            match = False

                            # TODO: Check if stats match
                            if stats:
                                item_stats = bot.get_item_stats(i.find_elements_by_tag_name("a")[0])
                                # FIXME: Accept all for now
                                match = True
                            else:
                                match = True

                            if match:
                                # Preview, Price, and Buy Now
                                goal_id.append(item_id)
                                goal_price.append(item_price) # Price is in span found in parent of i, cheat and use ".." notation XPath
                                goal_buy.append(buy_code)

                    # If our goal is not met
                    if not goal_id:
                        continue

                    # If our goal is met
                    else:
                        # PM the player
                        j = 0
                        while (result_counter != wanted) & (j > 0-len(goal_id)):
                            # debug
                            print(result_counter, "\n", wanted, "\n", j, "\n", str(0-len(goal_id)))
                            print(str(goal_id[j]), "\n", str(goal_price[j]), "\n", str(goal_buy[j]))
                            Owl.reply("Found Item(" + goal_id[j] + ") for " + goal_price[j] +"g. [Buy Now](" + goal_buy[j] + ")", client_name)
                            j -= 1
                            result_counter += 1
                            time.sleep(2) # chat ban prevention

                        # Mark success
                        logger.info("--- Goal met")
                        success = True
                        ready = query
                        #print("Counter: " + result_counter + ", wanted: " + wanted)
                        if(result_counter == wanted):
                            break;


                ## End of operation
                ## Tell user we're done
                # Return to main page
                try:
                    Owl.get("https://www.playinitium.com/main.jsp")
                except:
                    pass

                # Finally inform player of either successful or failed operation
                if success:
                    if result_counter == wanted:
                        Owl.reply("There you go!", client_name)
                    else:
                        Owl.reply("That's all I could find.", client_name)
                    logger.info("-Request completed successfully.", client_name)
                else:
                    if not stats:
                        Owl.reply("I couldn't find any "+goal+" for sale in "+Owl.get_location()+".", client_name)
                    else:
                        Owl.reply("I couldn't find any "+stats+" "+goal+"for sale in "+Owl.get_location()+".", client_name)
                    logger.warning("-Request failed.")

                ## Write statistics to CSV
                with open("../logs/stats.csv", 'a') as csvFile:
                    writer = csv.writer(csvFile)
                    data = [[time.asctime(), messages[0]['author'], goal, stats,  wanted, result_counter]]
                    writer.writerows(data)
                    csvFile.close()


            # This was a request for information
            else:
                # Prepare to write statistics to CSV
                csvFile = open("../logs/stats_requests.csv", 'a')
                writer = csv.writer(csvFile)
                if "HCF.NOW" in q:
                    logger.warning("HALT FLAG RECEIVED")
                    data = [[time.asctime(), authors[0], "HCF.NOW", q]]
                    writer.writerows(data)
                    csvFile.close()
                    sys.exit()
                if not success and "where" in q.lower():
                    # Tell them where we are.
                    Owl.reply("I am currently in "+Owl.get_location(), client_name)
                    read = messages[0]
                    success = True
                    data = [[time.asctime(), authors[0], "where", q]]
                if not success and "thank" in q.lower():
                    Owl.reply("You're welcome! :)", client_name)
                    read = messages[0]
                    success = True
                    data = [[time.asctime(), authors[0], "thanks", q]]
                if not success and "love you" in q.lower():
                    if authors[0] == "Hyren" or authors[0] == "Eliona" or authors[0] == "Aliona":
                        Owl.reply("<3", client_name)
                    else:
                        Owl.reply("Sorry, I'm taken. But you're sweet!", client_name)
                    read = messages[0]
                    success = True
                    data = [[time.asctime(), authors[0], "love", q]]
                if not success or "help" in q.lower():
                    # Tell them who we are.
                    Owl.reply("Hi there! I am a shop-searching bot controlled by Rade.", client_name)
                    Owl.reply("Try asking for an item like this: find 2 ornate orcish helm, or find all protector", client_name)
                    read = messages[0]
                    success = True
                    data = [[time.asctime(), authors[0], "help", q]]
                if success:
                    logger.info("Request completed succesfully.")
                writer.writerows(data)
                csvFile.close()


    logger.error("OUTSIDE WHILE TRUE LOOP!")
