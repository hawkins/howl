Owl
----

A python based bot for the browser game [initium](http://playinitium.com/) which interfaces with players through various chat channels, with the intent of searching shops for specific items on request.

Do note this bot is a work in progress, and as such may be a straight-up mess at any point in time. Code will be refined when resource constraints are met or when all features are stable.

##Dependencies
This bot was written using python3.4, and uses a firefox webdriver and selenium to intertact with dynamic webpages. This can be done in a headless style, which requires pyvirtualdisplay and xvfb.
```
sudo apt-get install firefox xvfb
sudo pip3 install selenium pytz tzlocal pyvirtualdisplay
```
This box is currently developed and supported on Ubuntu 14.04. 
This bot was tested on Arch linux in its early stages, but is no longer supported on Arch and is thus no longer guaranteed to work out-of-the-box.

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
```
./owl.py -h
./owl.py
./owl.py -l true
```
##Acknowledgements
Special thanks to CptSpaceToaster for sourcing the initial codebase. Also thanks to Bella and Havok for their occasional assistance in special case testing.
