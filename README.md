[![Owl](http://2.bp.blogspot.com/-GTsy_zjnqGc/UgsQGB_sfUI/AAAAAAAAAJ8/hsGWsylKsKA/s64/The_Owl_of_Minerva.png)](Owl)Owl - the free shop search bot for Initium[![Owl](http://2.bp.blogspot.com/-GTsy_zjnqGc/UgsQGB_sfUI/AAAAAAAAAJ8/hsGWsylKsKA/s64/The_Owl_of_Minerva.png)](Owl)
----

A python based bot framework for the browser game [initium](http://playinitium.com/) which interfaces with players through various chat channels.

Do note this project is a work in progress, and as such may be a straight-up mess at any point in time. Code will be refined when resource constraints are met or when all features are stable.

##Modules
Currently this project includes the following modules:
- Owl - a shop-searching bot for providing players with requested items found in the local merchant booths.
- Auctioneer - a bot for selling items to players for the highest price.
- and more to come! Feel free to submit your own in a pull request ;)

##Dependencies
This project was written using python3.4, and uses a firefox webdriver and selenium to intertact with dynamic webpages. This can be done in a headless style, which requires pyvirtualdisplay and xvfb.
```
sudo apt-get install firefox xvfb
sudo pip3 install selenium pytz tzlocal pyvirtualdisplay
```
This project is currently developed and supported on Ubuntu 14.04.
Originally, the Owl module was tested on Arch linux in its early stages, but is no longer supported on Arch and is thus no longer guaranteed to work out-of-the-box.

##Config File
You will need a config in the directory you run the bot.  It must be named `cfg.json`

Example `cfg.json`
```
{
    "email": "your-email@your.domain.com",
    "uname": "YourUsername",
    "pw": "YourPassword"
}
```

##Running
# Owl:
```
./owl.py -h
./owl.py
./owl.py -l true
```

In typical operation, players can private message Owl to search shops for items containing a string, shown here:
![Example image shown here](https://github.com/hawkins/owl/blob/master/img/preview.PNG)

##Acknowledgements
Special thanks to CptSpaceToaster for sourcing the original version of the initium module and configuration parser. Also thanks to Bella and Havok for their occasional assistance in preliminary special case testing.
