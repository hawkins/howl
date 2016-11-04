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
        # Hax
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
    log_file = "../logs/owl.log"
    logger = create_timed_rotating_log(log_file)

    try:
        Owl = Owl_Bot()
        DEF_MAX_RESULTS = 5
        wanted = -1 # How many results client wanted
        stats = None # Desired stats (weapon attack 0d0/0d00)

        logger.info("Current Location: " + Owl.get_location())

        # Download messages
        auths, texts = Owl.update_messages("Private")
        read = texts[0] # save latest message as read for base case
        logger.info("Marking read as \"" + read + "\"")
        logger.info("Now listening for requests")

        while True:
            # Reset success tag for user interaction
            success = False
            # Reset counter flag
            result_counter = 0
            wanted = 0
            stats = None

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

            # Rebuild list of PMs
            authors, queries = [], []
            while (len(authors) == 0):
                authors, queries = Owl.update_messages("Private")
                #print(authors)
                if (len(authors[0]) == 0):
                    authors, queries = [], []


            if (queries[0] != read) and (authors[0] != '[Bot] Owl'):
                query = queries[0]
                q = query.split("-> ")[1] # get text after to/from info
                logger.info("Query received from " + authors[0] + ": " + q)

                # Get a WebElement of the player who requested Owl
                client = Owl.find_elements_by_xpath('//div[@id="chat_messages_PrivateChat"]/div')[0].find_elements_by_class_name("chatMessage-private-nickname")[0]

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
                        Owl.reply(client, "Sorry, I don't understand. Did you forget a space?")
                        continue

                    logger.info("-Looking for:" + goal + "")

                    # Say "I'll get right on that!"
                    Owl.reply(client, "I'll get right on that!")

                    # Click on merchant box
                    Owl.find_elements_by_xpath('//div[@id="main-merchantlist"]/div')[0].click()

                    # Gather list of all shops
                    time.sleep(3) # could use a try block here
                    merchants = Owl.find_elements_by_class_name("main-merchant-container")

                    # Convert to links
                    temp = [] # This process uses a work around for WebElements and iterative for loops, which involves use of temp list variable
                    for each in merchants:
                        temp.append(each.find_elements_by_tag_name("div")[0].find_elements_by_tag_name("a")[0].get_attribute("href"))
                    merchants = temp

                    # Iterate through each previously made link
                    for each in merchants:
                        try:
                            logger.info("--Checking Merchant ID:" + each.split("Id=")[1])
                            Owl.get(each)
                        except:
                            logger.error("---An error occurred while loading the merchant.")

                        # Now that store is open, search for the item
                        items = [] # All items in store
                        goal_id = [] # ItemID for goal items (for preview)
                        goal_buy = [] # buy now links to goal items
                        goal_price = [] # prices for the goal item

                        for i in Owl.find_elements_by_class_name("main-item-container"):
                            if(len(i.find_elements_by_tag_name("div")) <= 0):
                                # Item has not been sold
                                # Get the item element
                                current_item = i.find_elements_by_tag_name("a")[0].get_attribute("innerHTML").split(">")[1].lower()

                                # If we found our goal
                                if goal in re.sub('(?!\s)[\W_]', '', current_item):
                                    match = False
                                    # Check if stats match
                                    if stats:
                                        i.find_elements_by_tag_name("a")[0].click()
                                        # Ensure the popup loads but we don't wait too long
                                        loaded = False
                                        while not loaded:
                                            try:
                                                elements = Owl.find_elements_by_class_name("main-item-subnote")
                                                if elements[0].get_attribute("innerHTML").lower() == stats:
                                                    # Item stats match
                                                    match = True
                                                loaded = True
                                            except:
                                                pass
                                    else:
                                        match = True
                                    if match:
                                        # Preview, Price, and Buy Now
                                        items.append(re.sub('(?!\s)[\W_]', '', current_item))
                                        goal_id.append(i.find_elements_by_tag_name("a")[0].get_attribute("rel").split("itemId=")[1])
                                        goal_price.append(i.find_elements_by_xpath("..")[0].find_elements_by_tag_name("span")[0].text) # Price is in span found in parent of i, cheat and use ".." notation XPath
                                        goal_buy.append(i.find_elements_by_tag_name("a")[1].get_attribute("onclick"))

                        # If our goal is not met
                        if not any(goal in i for i in items):
                            #logger.warning("--Goal not met, checking next page")
                            continue

                        # If our goal is met
                        else:
                            # Return to main page
                            try:
                                Owl.get("https://www.playinitium.com/main.jsp")
                            except:
                                pass

                            # PM player
                            j = 0
                            while (result_counter != wanted) & (j > 0-len(goal_id)):
                                # debug
                                print(result_counter, "\n", wanted, "\n", j, "\n", str(0-len(goal_id)))
                                print(str(goal_id[j]), "\n", str(goal_price[j]), "\n", str(goal_buy[j]))
                                Owl.reply(client, "Found Item(" + goal_id[j] + ") for " + goal_price[j] +"g. [Buy Now](" + goal_buy[j])
                                j -= 1
                                result_counter += 1
                                time.sleep(2) # chat ban prevention

                            # Mark success
                            logger.info("---Goal met")
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
                            Owl.reply(client, "There you go!")
                        else:
                            Owl.reply(client, "That's all I could find.")
                        logger.info("-Request completed successfully.")
                    else:
                        if not stats:
                            Owl.reply(client, "I couldn't find any "+goal+" for sale in "+Owl.get_location()+".")
                        else:
                            Owl.reply(client, "I couldn't find any "+stats+" "+goal+"for sale in "+Owl.get_location()+".")
                        logger.warning("-Request failed.")

                    ## Write statistics to CSV
                    with open("../logs/stats.csv", 'a') as csvFile:
                        writer = csv.writer(csvFile)
                        data = [[time.asctime(), authors[0], goal, stats,  wanted, result_counter]]
                        writer.writerows(data)
                        csvFile.close()


                # Request for information
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
                        Owl.reply(client, "I am currently in "+Owl.get_location())
                        read = queries[0]
                        success = True
                        data = [[time.asctime(), authors[0], "where", q]]
                    if not success and "thank" in q.lower():
                        Owl.reply(client, "You're welcome! :)")
                        read = queries[0]
                        success = True
                        data = [[time.asctime(), authors[0], "thanks", q]]
                    if not success and "love you" in q.lower():
                        if authors[0] == "Hyren" or authors[0] == "Eliona" or authors[0] == "Aliona":
                            Owl.reply(client, "<3")
                        else:
                            Owl.reply(client, "Sorry, I'm taken. But you're sweet!")
                        read = queries[0]
                        success = True
                        data = [[time.asctime(), authors[0], "love", q]]
                    if not success or "help" in q.lower():
                        # Tell them who we are.
                        Owl.reply(client, "Hi there! I am a shop-searching bot controlled by Rade.")
                        Owl.reply(client, "Try asking for an item like this: find 2 ornate orcish helm, or find all protector")
                        read = queries[0]
                        success = True
                        data = [[time.asctime(), authors[0], "help", q]]
                    if success:
                        logger.info("Request completed succesfully.")
                    writer.writerows(data)
                    csvFile.close()


        logger.error("OUTSIDE WHILE TRUE LOOP!")




    except (ConnectionRefusedError, KeyboardInterrupt) as e:
        if type(e) is KeyboardInterrupt:
            print("")
        if type(e) is ConnectionRefusedError:
            logger.error("Connection to the Firefox Webdriver was lost")
        print("Exiting")
        sys.exit(0)
