#!/usr/bin/python3
# System
import argparse
import sys
import os
import time
import json
from pyvirtualdisplay import Display
import selenium.common.exceptions
# Local
import initium
import string
import re


class Owl_Bot(initium.webdriver):
    def __init__(self):
        self.cfg = self._parse_config()

        print("Initializing webdriver")
        # Hax
        super().__init__()

        print("Connecting to Initium")
        self.get("http://www.playinitium.com")

        print("Logging in as {0}".format(self.cfg["uname"]))
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
        print('Parsing command line arguments')
        self._parser = argparse.ArgumentParser(description="Owl - A Python based bot for Initium - http://playinitium.com")
        self._parser.add_argument("-c", "--config", dest="config_file", default="cfg.json",
                                  help="Configuration to use (default=cfg.json)")
        self._parser.add_argument("-d", "--do_chat", dest="do_chat", action="store_true",
                                  help="Handle commands in each rooms local chat")
        self._parser.add_argument('-m', '--map', dest='map_file', default='map.json',
                                  help='Map file to use (default=map.json)')
        self._parser.add_argument('-l', '--headless', help='Run in headless operation mode if HEADLESS=true/True/T')
        self.args = self._parser.parse_args()
        if self.args.headless == 'true' or self.args.headless == 'True' or self.args.headless == 'T' or self.args.headless == 'TRUE':
            display = Display(visible=0, size=(800,600))
            display.start()

        print("Reading config")

        if os.path.isfile(self.args.config_file):
            with open(self.args.config_file, encoding="utf-8") as data_file:
                return json.loads(data_file.read())
        else:
            print("Error: Config: {0} not found".format(self.args.config_file))
            sys.exit(1)

    def say(self, ChatTab="Location", Text="Uh oh! Something went wrong."):
        ## Says a message in the given chat tab
        ## Can print multiple messages by separating with '\n'
        # Click appropriate chat tab
        for button in Owl.find_elements_by_class_name("chat_tab"):
            if button.text.lower() == ChatTab.lower():
                button.click()
        # Split Text into multiple lines by \n
        Texts = Text.split('\n')
        # Reply each text from Texts
        for each in Texts:
            Owl.find_element_by_id("chat_input").send_keys(each)
            Owl.find_element_by_id("chat_submit").click()
            time.sleep(0.25)



    def reply(self, PlayerNameElement=None, Text="Uh oh! Something went wrong."):
        ## Replies through private chat
        ## Requires Private chat tab to already be open
        ## Assumes player name already selected if PlayerNameElement is not given
        # Click player name and then Private Chat
        try:
            PlayerNameElement.click()
            loaded = False
            while not loaded:
                try:
                    self.find_elements_by_class_name("mini-window-header-split")[0].find_element_by_link_text("Private Chat").click() # Click "Private Chat"
                    loaded = True
                except IndexError:
                    pass
            loaded = False
        except:
            # Assumes player already in private chat
            pass

        # Split Text into multiple lines by \n
        Texts = Text.split('\n')
        # Reply each text from Texts
        for each in Texts:
            Owl.find_element_by_id("chat_input").send_keys(each)
            Owl.find_element_by_id("chat_submit").click()
            time.sleep(0.25)

    def update_messages(self, ChatTab="Private"):
        ## Load messages and return an array of [Authors[], Queries[]]
        ## Would be ideal to return by reference, but alas.
        # Return variables here for scope:
        Authors = []
        Queries = []
        # Click appropriate chat tab
        for button in Owl.find_elements_by_class_name("chat_tab"):
            if button.text.lower() == ChatTab.lower():
                button.click()
        # Rebuild list of PMs, in while & try block to ensure success once loaded
        loaded = False
        while not loaded:
            try:
                if ChatTab.lower() == "global":
                    Messages = self.find_elements_by_xpath('//div[@id="chat_messages_GlobalChat"]/div')
                if ChatTab.lower() == "location":
                    Messages = self.find_elements_by_xpath('//div[@id="chat_messages_LocationChat"]/div')
                if ChatTab.lower() == "private":
                    Messages = self.find_elements_by_xpath('//div[@id="chat_messages_PrivateChat"]/div')

                for each in Messages:
                    try:
                        Authors.append(each.find_elements_by_class_name("chatMessage-text")[0].text)
                        Queries.append(each.find_elements_by_class_name("chatMessage-text")[1].text)
                    except KeyboardInterrupt:
                        print("Received KeyboardInterrupt")
                        sys.exit()
                    except:
                        print("Did a DEV pm us?")
                        # Following snippet designed to fit Bella's somewhat arbitraary standards
                        Authors.append(each.find_elements_by_class_name("chatMessage-text")[0].find_elements_by_xpath('//a//font/span').text)
                        Queries.append(each.find_elements_by_class_name("chatMessage-text")[1].text)
                Queries[0] # Generates IndexError if messages not yet loaded
                loaded = True
            except:
                pass
        loaded = False

        # Ugh... Wish we could return by reference more simply
        return [Authors, Queries]


if __name__ == "__main__":
    try:
        Owl = Owl_Bot()
        DEF_MAX_RESULTS = 5

        print("Current Location: " + Owl.get_location())

        # Download messages
        auths, texts = Owl.update_messages("Private")
        read = texts[0] # save latest message as read for base case
        print("Marking read as \"" + read + "\"")
        print("Now listening for requests")

        while True:
            # Reset success tag for user interaction
            success = False
            # Reset counter flag
            result_counter = 0

            # Check location tab for "hoot" or " owl" in last message
            hootauth, hootmsg = Owl.update_messages("Location")
            for each in hootmsg[0:4]:
                if "Hoot hoot! I am Owl. PM me to search shops!" not in each:
                    if "hoot" in each.lower():
                        Owl.say("Location", "Hoot hoot! I am Owl. PM me to search shops!")
                        print("Completed hoot request!")
                        break
                    if " owl" in each.lower():
                        Owl.say("Location", "Hoot hoot! I am Owl. PM me to search shops!")
                        print("Completed hoot request!")
                        break
                else:
                    break

            # DEBUG
            #print("Q[0]: " + queries[0])
            #print("Read: " + read)
            #print("A[0]: " + authors[0])

            # Rebuild list of PMs
            authors, queries = [], []

            #print ("Attempting to prevent \"q = query.split(\"-> \")[1] IndexError\" which occurs after every successful command, and occasionally on startup")
            while (len(authors) == 0):
                authors, queries = Owl.update_messages("Private")
                print(authors)
                if (len(authors[0]) == 0):
                    authors, queries = [], []


            if (queries[0] != read) and (authors[0] != '[Bot] Owl'):
                query = queries[0]
                q = query.split("-> ")[1] # get text after to/from info
                print("Query received from ", authors[0], ": ", q)

                # Get a WebElement of the player who requested Owl
                client = Owl.find_elements_by_xpath('//div[@id="chat_messages_PrivateChat"]/div')[0].find_elements_by_class_name("chatMessage-text")[0]

                if "find" in q.lower():
                    # Identify the item
                    goal = ' '.join(q.split("ind ")[1].split()).lower()
                    goal = re.sub('(?!\s)[\W_]', '', goal)
                    print("-Looking for:", goal, "")

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

                    # iterate through each previously made link
                    for each in merchants:
                        try:
                            print("--Checking Merchant ID:" + each.split("Id=")[1])
                            Owl.get(each)
                        except:
                            print("---An error occurred while loading the merchant.")

                        # Now that store is open, search for the item
                        items = []
                        for i in Owl.find_elements_by_class_name("main-item-container"):
                            current_item = i.find_elements_by_tag_name("a")[0].get_attribute("innerHTML").split(">")[1].lower()
                            items.append(re.sub('(?!\s)[\W_]', '', current_item))

                        # If our goal is not met
                        if not any(goal in i for i in items):
                            #print("--Goal not met, checking next page")
                            continue

                        # If our goal is met
                        else:
                            url = Owl.current_url
                            # Return to main page
                            try:
                                Owl.get("https://www.playinitium.com/main.jsp")
                            except:
                                pass

                            ## PM player
                            # Rebuild list of PMs
                            #authors, queries = Owl.update_messages("Private")

                            # Inform player of success
                            Owl.reply(client, "Found the item here: "+url) # should be request, not client

                            # Mark success
                            print("--Goal met")
                            success = True
                            ready = query
                            result_counter += 1
                            if(result_counter == DEF_MAX_RESULTS):
                                break;
                            # break # disabled so we search every shop for the item

                    ## End of operation
                    ## Tell user we're done
                    # Return to main page
                    try:
                        Owl.get("https://www.playinitium.com/main.jsp")
                    except:
                        pass

                    # Finally inform player of either successful or failed operation
                    if success:
                        if result_counter == DEF_MAX_RESULTS:
                            Owl.reply(client, "That should be enough for now.")
                        else:
                            Owl.reply(client, "That's all I could find.")
                        print("-Request completed successfully.")
                    else:
                        Owl.reply(client, "I couldn't find any "+goal+" in "+Owl.get_location()+".")
                        print("-Request failed.")


                # Request for information
                else:
                    if "HCF.NOW" in q:
                        print("********\nHALT FLAG RECEIVED\n********")
                        sys.exit()
                    if not success and "where" in q.lower():
                        # Tell them where we are.
                        Owl.reply(client, "I am currently in "+Owl.get_location())
                        read = queries[0]
                        success = True
                    if not success and "thank" in q.lower():
                        Owl.reply(client, "You're welcome! :)")
                        read = queries[0]
                        success = True
                    if not success and "love you" in q.lower():
                        if authors[0] == "DiqFuqis" or authors[0] == "Eliona" or authors[0] == "Aliona":
                            Owl.reply(client, "<3")
                        else:
                            Owl.reply(client, "Sorry, I'm taken. But you're sweet!")
                        read = queries[0]
                        success = True
                    if not success or "help" in q.lower():
                        # Tell them who we are.
                        Owl.reply(client, "Hi there! I am a shop-searching bot controlled by Rade.")
                        Owl.reply(client, "Try asking for an item like this: find ornate orcish helm")
                        read = queries[0]
                        success = True
                    if success:
                        print("Request completed succesfully.")


        print("OUTSIDE WHILE TRUE LOOP!")




    except (ConnectionRefusedError, KeyboardInterrupt) as e:
        if type(e) is KeyboardInterrupt:
            print("")
        if type(e) is ConnectionRefusedError:
            print("Connection to the Firefox Webdriver was lost")
        print("Exiting")
        sys.exit(0)
