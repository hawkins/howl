#!/usr/bin/python3.4
from selenium.webdriver import Chrome as webdriver
from selenium.common.exceptions import NoSuchElementException
import time

class initium(object):
    """
    This is the core Howl framework object.

    All bot modules should inerhit from this class by using:

    >>> class Bot(initium.webdriver, initium.initium): # Class definition line for Bot implementing Howl framework
    """
    def login(self, email, pw):
        """
        This function logs the player in to the Initium world.

        Args:
            email (string) -- Username to log in with
            pw (string) -- Password to log in with

        Returns:
            None: This function return is void
        """
        # Load front page
        self.get('http://www.playinitium.com')

        # Click login signup switch
        self.find_element_by_class_name('login-signup-switch').find_element_by_tag_name('a').click()

        # Enter email
        login = self.find_elements_by_name("email")[1]
        login.send_keys(self.cfg["email"])

        # Enter password
        login = self.find_elements_by_name("password")[1]
        login.send_keys(self.cfg["pw"])

        # Click login
        for button in self.find_elements_by_class_name("big-link"):
            if button.text == "Login":
                button.click()
                break

    def get_location(self):
        """
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


    def get_gold(self):
        """
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
            return -1

    def say(self, text, chat_tab="Location", delay=True):
        """
        This function says a message in the specified chat tab. Multiple messages can be said by separating them with newline characters.

        Do be wary of multiple messages at once tho, as too many sent too quickly can result in a temporary chat ban in-game.

        Args:
            text (string) -- Actual message to be said in chat.

            chat_tab (string) -- Global, Location, Party, Group, or Private (Note, Initium.reply should be used for private). Default is "Location"

            delay (boolean) -- Delay between sending messages or not. Default is True

        Returns:
            Nothing is returned by this function.

        Examples of this function in use:

        >>> Bot.say("Using Howl is easy!", "Global") # "Using Howl is easy!" in Global tab
        >>> Bot.say("This Message splits \\n Into two chat messages.", "Location") # "This message splits ", " Into two chat messages." both in Location tab
        """
        # Click appropriate chat tab
        for button in self.find_elements_by_class_name("chat_tab"):
            if chat_tab.lower() in button.text.lower():
                button.click()
                break

        # Split Text into multiple lines by \n
        texts = text.split('\n')

        # Send each text from Texts
        for each in texts:
            self.find_element_by_id("chat_input").send_keys(each)
            self.find_element_by_id("chat_submit").click()

            # Delay if requested
            if delay:
                time.sleep(0.25)

    def reply(self, text, player=None, delay=True):
        """
        This replies to a player with a certain message in the Private chat tab. Multiple messages can be said by separating them with newline characters.

        Do be wary of multiple messages at once tho, as too many sent too quickly can result in a temporary chat ban in-game.

        Assumes player name already selected if player is not given.

        Args:
            text (string) -- Actual message to be said to player.

            player (string) -- Target player's name.

            delay (boolean) -- Delay between sending messages or not. Default is True

        Returns:
            Nothing is returned by this function.

        Examples of this function in use:

        >>> Bot.reply("Using Howl is easy!", "[Dev] Rade") # "Using Howl is easy!" whispered to whichever player's name is in PlayerNameElement
        >>> Bot.reply("This Message splits \\n Into two chat messages.", "Bella") # "This message splits ", " Into two chat messages." both said to the given player
        >>> Bot.reply("Something here.") # "Something here" said in private chat, assuming player name was already selected for private chat.
        """
        # Click appropriate chat tab
        for button in self.find_elements_by_class_name("chat_tab"):
            if 'private' in button.text.lower():
                button.click()
                break

        # Wait until messages have loaded
        while not self.is_chat_tab_loaded('Private'):
            pass

        # Gather messages
        messages = self.find_elements_by_xpath('//div[@id="chat_messages_PrivateChat"]/div')

        # Click player name
        found = False
        for message in messages:
            # Get author of message
            author = message.find_element_by_class_name('chatMessage-private-nickname')

            # If author matches target
            if author.text == player:
                # Click player name element
                author.click()

                # Delay for server
                time.sleep(1)

                found = True
                break

        # Raise error if player not found
        if not found:
            raise Exception('Unable to locate player %s in private chat authors' % player)

        # Split Text into multiple lines by \n
        texts = text.split('\n')

        # Reply each text from Texts
        for each in texts:
            self.find_element_by_id('chat_input').send_keys(each)
            self.find_element_by_id('chat_submit').click()

            # Delay if requested
            if delay:
                time.sleep(0.25)

    def get_chat_messages(self, chat_tab='Private'):
        """
        This function opens the specified chat tab and collects all messages and authors in the chat.

        Args:
           chat_tab (string) -- Global, Location, Party, Group, or Private. Default is "Private"

        Returns:
           messages (array) -- An array of dictionaries containing keys 'time', 'author', 'text', 'channel'.

        One way to use this function is:

        messages = Bot.update_messages("Global")
        """
        # Return variable here for scope:
        messages = []

        # Raise exception if illegal chat tab requested
        if chat_tab not in ['Global', 'Private', 'Location', 'Group', 'Party']:
            raise Exception('Error: illegal chat tab %s. Must be \'Global\', \'Location\', \'Party\', \'Private\', ' % chat_tab)

        # Click appropriate chat tab
        self.find_element_by_id(chat_tab + 'Chat_tab').click()

        # Wait until messages are loaded
        while not self.is_chat_tab_loaded(chat_tab):
            pass

        message_elements = self.find_elements_by_xpath('//div[@id="chat_messages_%sChat"]/div' % chat_tab)

        # If messages were found, iterate over them
        if message_elements:
            for each in message_elements:
                # Skip greeting messages
                if "A new player has just joined Initium" in each.text:
                    continue

                # Add message
                if chat_tab == 'Private':
                    msg = { 'time': each.find_elements_by_tag_name('span')[0].text,
                            'author': each.find_element_by_class_name('chatMessage-private-nickname').text,
                            'text': each.find_element_by_class_name('chatMessage-text').text.split('-> ', 1)[1],
                            'channel': chat_tab}
                else:
                    msg = { 'time': each.find_elements_by_tag_name('span')[0].text,
                            'author': each.find_elements_by_tag_name('span')[1].text,
                            'text': each.find_elements_by_tag_name('span')[2].text[2:],
                            'channel': chat_tab}

                messages.append(msg)


        # Return a list of 3-item tuples
        return messages
        return list(zip(authors, texts, times))

    def get_item_stats(self, element=None):
        """
        This function parses the popup HTML for relevant item stats.
        Optionally receives an argument `element` to click before loading stats, otherwise assumes an item popup is opened.

        Args:
            element (selenium.WebElement) -- Optionally click this element to load its item stats

        Returns:
            stats (dictionary) -- A mapping of string keys to their respective stats. Empty if no popup is open

        One way to use this function is:

        >>> item_stats = Bot.get_item_stats(item_web_element) # Fills the dictionary with all relevant stats
        """
        # Dictionary to return
        stats = {}

        # Click the element if provided
        if element:
            element.click()

        # Wait until item popup loads
        while not self.is_item_popup_open():
            pass

        # Load all item stat elements
        elements = self.find_elements_by_class_name('item-popup-field')

        # First item is name
        stats['name'] = elements[0].find_element_by_tag_name('div').text

        # Iterate over all
        for stat_element in elements:
            name = stat_element.get_attribute('name')
            if name:
                stats[name] = stat_element.find_element_by_tag_name('div').text

        return stats

    def is_item_popup_open(self):
        """
        Checks for existance of an item popup with stats visible.

        Args:
            None - This function receives no arguments

        Returns:
            result (boolean) -- True if an item popup is loaded
        """
        try:
            # Attempt to find elements by class name
            elements = self.find_elements_by_class_name('item-popup-field')

            # Return true if text is loaded
            if elements[0].text != '':
                return True
        except:
            # If an exception occurred, item not open
            return False

    def is_chat_tab_loaded(self, chat_tab='Location'):
        """
        Checks for existance of messages in the given chat tab.

        Args:
            chat_tab (strng) -- The chat tab to select. Default is \'Location\'

        Returns:
            result (boolean) -- True if an item popup is loaded
        """
        # Raise exception if illegal chat tab requested
        if chat_tab not in ['Global', 'Private', 'Location', 'Group', 'Party']:
            raise Exception('Error: illegal chat tab %s. Must be \'Global\', \'Location\', \'Party\', \'Private\', ' % chat_tab)

        try:
            # Attempt to find elements
            messages = self.find_elements_by_xpath('//div[@id="chat_messages_%sChat"]/div' % chat_tab)
        except:
            # If an exception occurred, messages were not found so return False
            return False


        # If no exception occurred, messages were found so return True
        return True

    def send_keypresses(self, keys):
        """
        Send keys to the page.

        Args:
            keys (string) -- String of keys to be pressed

        Returns:
            Nothing is returned by this function
        """
        self.find_element_by_xpath('//body').send_keys(keys)
