[![Owl](http://2.bp.blogspot.com/-GTsy_zjnqGc/UgsQGB_sfUI/AAAAAAAAAJ8/hsGWsylKsKA/s64/The_Owl_of_Minerva.png)](Owl)Howl - the free bot framework for Initium[![Owl](http://2.bp.blogspot.com/-GTsy_zjnqGc/UgsQGB_sfUI/AAAAAAAAAJ8/hsGWsylKsKA/s64/The_Owl_of_Minerva.png)](Owl)
----

A python based bot framework for the browser game [initium](http://playinitium.com/) which provides an interface for players to interact with and control the bot through various in-game chat channels.


## Modules

Currently this project includes the following modules:

- Owl - a shop-searching bot for providing players with requested items found in the local merchant booths.
- Auction - a bot for selling items to players for the highest price.
- Records - a stat-tracking bot to record the best items

and more to come! Feel free to submit your own in a pull request ;)


## Dependencies

This project was written using Python 3.4, and uses a Google Chrome webdriver and `selenium` to interact with dynamic webpages. This can be done in a headless style, which requires `pyvirtualdisplay` and `xvfb`.

You'll need to install Chrome's WebDriver per [Google's instructions](https://sites.google.com/a/chromium.org/chromedriver/getting-started).

Afterwards, install the remaining dependencies via command line:

```
sudo apt-get install xvfb
sudo pip3 install selenium pytz tzlocal pyvirtualdisplay
```


## Config File

You will need a config in the directory you run the bot.  It must be named `cfg.json`

Example `cfg.json`
```
{
    "email": "your-email@your.domain.com",
    "uname": "YourUsername",
    "pw": "YourPassword"
}
```


## Running

# Owl:

```
./owl.py -h
./owl.py
./owl.py -l
```

In typical operation, players can private message Owl to search shops for items containing a string, shown here:
![Example image shown here](https://github.com/hawkins/owl/blob/master/img/preview.PNG)


## Acknowledgements

Special thanks to CptSpaceToaster for sourcing the original version of the initium module and configuration parser. Also thanks to Bella and Havok for their occasional assistance in preliminary special case testing.
