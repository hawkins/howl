#!/usr/bin/python3.4
# System
from selenium.webdriver import Firefox
from selenium.common.exceptions import NoSuchElementException

# Let others know what class we're monkey patching
# They can extend initum.webdriver then
webdriver = Firefox


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
