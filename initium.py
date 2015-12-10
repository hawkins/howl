#!/usr/bin/python3.4
# System
from selenium.webdriver import Firefox
from selenium.common.exceptions import NoSuchElementException
import time

# Let others know what class we're monkey patching
# They can extend initum.webdriver then
webdriver = Firefox

class initium(object):
    def get_location(self):
        try:
            elem = self.find_element_by_class_name("header-location")
            if elem:
                if elem.text:
                    return elem.text
        except NoSuchElementException:
            # Not found
            pass
    Firefox.get_location = get_location


    def get_gold(self):
        try:
            elem = self.find_element_by_class_name("header-stats")
            if elem:
                if elem.text:
                    stats = elem.text.split()
                    if len(stats) > 1:
                        return stats[1]
        except NoSuchElementException:
            # Not found
            pass
    Firefox.get_gold = get_gold

    def say(self, ChatTab="Location", Text="Uh oh! Something went wrong."):
        ## Says a message in the given chat tab
        ## Can print multiple messages by separating with '\n'
        # Click appropriate chat tab
        for button in self.find_elements_by_class_name("chat_tab"):
            if button.text.lower() == ChatTab.lower():
                button.click()
        # Split Text into multiple lines by \n
        Texts = Text.split('\n')
        # Reply each text from Texts
        for each in Texts:
            self.find_element_by_id("chat_input").send_keys(each)
            self.find_element_by_id("chat_submit").click()
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
            self.find_element_by_id("chat_input").send_keys(each)
            self.find_element_by_id("chat_submit").click()
            time.sleep(0.25)

    def update_messages(self, ChatTab="Private"):
        ## Load messages and return an array of [Authors[], Queries[]]
        ## Would be ideal to return by reference, but alas.
        # Return variables here for scope:
        Authors = []
        Queries = []
        # Click appropriate chat tab
        for button in self.find_elements_by_class_name("chat_tab"):
            if ChatTab.lower() in button.text.lower():
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
