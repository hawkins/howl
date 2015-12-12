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


class Auction_Bot(initium.webdriver, initium.initium):
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


if __name__ == "__main__":
    try:
        auctioneer = Auction_Bot()

        print("Current Location: " + auctioneer.get_location())

        # Download messages
        auths, texts = Owl.update_messages("Global")
        # Mark as read
        print("Now listening for requests")

        while True:
            # Check for request
            for index, text in enumerate(texts, start=0):
                if "start bid" in texts[index]:

                if index == 5: # Only check 6 most recent messages
                    break

            # Update messages
            auths, texts = Owl.update_messages("Global")


        print("OUTSIDE WHILE TRUE LOOP!")




    except (ConnectionRefusedError, KeyboardInterrupt) as e:
        if type(e) is KeyboardInterrupt:
            print("")
        if type(e) is ConnectionRefusedError:
            print("Connection to the Firefox Webdriver was lost")
        print("Exiting")
        sys.exit(0)
