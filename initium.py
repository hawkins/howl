#!/usr/bin/python3.4
# System
from selenium.webdriver import Firefox
from selenium.common.exceptions import NoSuchElementException
import time

# Let others know what class we're monkey patching
# They can extend initum.webdriver then
webdriver = Firefox

class initium(object):
    """
    This is the core Howl framework object.

    All bot modules should inerhit from this class by using:

    >>> class Bot(initium.webdriver, initium.initium): # Class definition line for Bot implementing Howl framework
    """
    def get_location(self):
        """
        ###get_location(self):

        This function returns the current location of the bot in the Initium world.

        Args:
           None: This function takes no arguments

        Returns:
           Location (string) -- Either actual location or "Unknown Location" if location could not be found.

        One way to use this function is:

        >>> print("Location: " + Bot.get_location())
        Location: Aera
        """
        try:
            elem = self.find_element_by_class_name("header-location")
            if elem:
                if elem.text:
                    return elem.text
        except NoSuchElementException:
            # Not found
            return "Unknown Location"
    Firefox.get_location = get_location


    def get_gold(self):
        """
        ##get_gold(self):


        This function returns the current gold in the bot's inventory in the Initium game.

        Args:
           None: This function takes no arguments

        Returns:
           Gold (string) -- Either actual gold or "-1" if gold could quantitiy not be found.

        One way to use this function is:

        >>> print("Gold: " + Bot.get_gold())
        Gold: 9,873
        """
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
        """
        ##say(self, ChatTab="Location", Text="Uh oh! Something went wrong."):


        This function says a message in the specified chat tab. Multiple messages can be said by separating them with newline characters.

        Do be wary of multiple messages at once tho, as too many sent too quickly can result in a temporary chat ban in-game.

        Args:
           ChatTab (string) -- Global, Location, Party, Group, or Private (Note, Initium.reply should be used for private). Default is "Location"

           Text (string) -- Actual message to be said in chat. Default is "Uh oh! Something went wrong."

        Returns:
           Nothing is returned by this function.

        Examples of this function in use:

        >>> Bot.say("Global", "Using Howl is easy!") # "Using Howl is easy!" in Global tab
        >>> Bot.say("Location", "This Message splits \\n Into two chat messages.") # "This message splits ", " Into two chat messages." both in Location tab
        >>> Bot.say() # "Uh oh! Something went wrong." in Location tab
        """
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
        """
        ##reply(self, PlayerNameElement=None, Text="Uh oh! Something went wrong."):


        This replies to a player with a certain message in the Private chat tab. Multiple messages can be said by separating them with newline characters.

        Do be wary of multiple messages at once tho, as too many sent too quickly can result in a temporary chat ban in-game.

        Assumes player name already selected if PlayerNameElement is not given.

        Args:
           PlayerNameElement (Selenium.WebElement) -- A WebElement object of the link to the players name. I.e., clicking on this would popup the player's profile where players could click "Private Chat" to message the player privately.

           Text (string) -- Actual message to be said to player. Default is "Uh oh! Something went wrong."

        Returns:
           Nothing is returned by this function.

        Examples of this function in use:

        >>> Bot.reply(PlayerNameElement, "Using Howl is easy!") # "Using Howl is easy!" whispered to whichever player's name is in PlayerNameElement
        >>> Bot.reply(PlayerNameElement, "This Message splits \\n Into two chat messages.") # "This message splits ", " Into two chat messages." both said to the given player
        >>> Bot.reply(Text="Something here.") # "Something here" said in private chat, assuming player name was already selected for private chat.
        """
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
        """
        ##update_messages(self, ChatTab="Private"):


        This function opens the specified chat tab and collects all messages and authors in the chat.

        Args:
           ChatTab (string) -- Global, Location, Party, Group, or Private (Note, Initium.reply should be used for private). Default is "Private"

        Returns:
           Results (two-dimensional array) -- A two-dimensional array of [Authors[...], Queries[...]] containing the array of Authors who said which Queries in the specified ChatTab.

        One way to use this function is:

        >>> authors, messages = [], [] # initializes the blank arrays
        >>> authors, messages = Bot.update_messages("Global") # Fills the arrays appropriatly with chat messages from "Global" tab.
        """
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
                    except:
                        print("An exception occurred, closing...")
                        return 0 # return 0 to terminate the module (TyoeError: int is not iterable)
                Queries[0] # Generates IndexError if messages not yet loaded
                loaded = True
            except:
                pass
        loaded = False

        # Wish we could return by reference more simply
        return [Authors, Queries]

    def get_item_stats(self):
        """
        ##get_item_stats(self):


        This function assumes that an item was clicked in-game by the bot and then parses the popup HTML for relevant item stats.

        Args:
           None: This function takes no arguments

        Returns:
           stat_dictionary (dictionary):
              'Dice Quantity' (int) -- Default 0

              'Dice Sides' (int) -- Default 0

              'Critical Chance' (float) -- Default 0.00

              'Critical Multiplier' (int) -- Default 0

              'Block Chance' (int) -- Default 0

              'Damage Reduction' (int) -- Default 0

              'Dexterity Penalty' (int) -- 0

              'Item Type' (string) -- Default (NoneType) None

        One way to use this function is:

        >>> item_stats = {} # initializes the blank dictionary
        >>> item_web_element.click() # Click the item so the popup is created and displayed
        >>> item_stats = Bot.get_item_stats() # Fills the dictionary with all relevant stats
        >>> block_chance = item_stats['Block Chance'] # Assigns Block Chance value to block_chance variable (now integer)
        """
        ## Read popup HTML and return a dictionary of all item stats
        stat_dictionary = {
                            'Dice Quantity': 0,
                            'Dice Sides': 0,
                            'Critical Chance': 0.00,
                            'Critical Multiplier': 0,
                            'Block Chance': 0,
                            'Damage Reduction': 0,
                            'Dexterity Penalty': 0,
                            'Item Type': None
                            }
        # Sleep 2 seconds for page load
        time.sleep(2)

        ## First determine what type of item it is
        # Check <p> tag in popup
        paragraph_element = self.find_elements_by_xpath('//div[contains(@class,"cluetip-inner") and contains(@class, "ui-widget-content") and contains(@class, "ui-cluetip-content")]/div[@class="main-page"]/p')[0]
        #paragraph_element = paragraph_element.find_elements_by_class_name("main-page")[0].find_elements_by_tag_name("p")[0]
        paragraph_text = paragraph_element.get_attribute("innerHTML").lower()
        # Weapon or Armor?
        if "weapon" in paragraph_text:
            stat_dictionary['Item Type'] = "Weapon"
        else:
            if "armor" in paragraph_text:
                if "shirt" in paragraph_text:
                    stat_dictionary['Item Type'] = "Shirt Armor"
                else:
                    stat_dictionary['Item Type'] = "Armor"
            else:
                if "shield" in paragraph_text:
                    stat_dictionary['Item Type'] = "Shield"
                else:
                    stat_dictionary['Item Type'] = "Non-equipment"
                    # If it is not equipment then this function is useless.
                    return

        # Build stat list
        elements = self.find_elements_by_class_name("main-item-subnote")

        ## Armor Stats
        if "Armor" in stat_dictionary['Item Type'] or "Shield" in stat_dictionary['Item Type']:
            ## Try to solve block chance
            try:
                stat_dictionary['Block Chance'] = int(elements[0].get_attribute("innerHTML").split("%")[0])
            except Exception as e:
                print("Error: " + str(e))
            ## Try to solve damage Reduction
            try:
                stat_dictionary['Damage Reduction'] = int(elements[1].get_attribute("innerHTML"))
            except Exception as e:
                print("Error: " + str(e))
            ## Try to solve dexterity penalty
            try:
                stat_dictionary['Dexterity Penalty'] = int(elements[2].get_attribute("innerHTML").split("%")[0])
            except Exception as e:
                print("Error: " + str(e))

        ## Weapon Stats
        if "Weapon" in stat_dictionary['Item Type']:
            ## Try to solve dice quantity
            try:
                stat_dictionary['Dice Quantity'] = int(elements[0].get_attribute("innerHTML").split("D")[0])
            except Exception as e:
                print("Error: " + str(e))
            ## Try to solve dice sides
            try:
                stat_dictionary['Dice Sides'] = int(elements[0].get_attribute("innerHTML").split("D")[1])
            except Exception as e:
                print("Error: " + str(e))
            ## Try to solve critical chance
            try:
                stat_dictionary['Critical Chance'] = float(elements[1].get_attribute("innerHTML").split("%")[0])
            except Exception as e:
                print("Error: " + str(e))
            ## Try to solve critical Multiplier
            try:
                stat_dictionary['Critical Multiplier'] = float(elements[2].get_attribute("innerHTML").split("x")[0])
            except Exception as e:
                print("Error: " + str(e))
        return stat_dictionary
