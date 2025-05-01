# Javascript Websites Search Widget

This search widget takes takes a list of website urls and makes the content on them searchable through an embeddable javascript widget

- Converts a text file list of website urls to Markdown files of all of the information on the website
- Converts those Markdown files to a SQLite database with a full text search table
- Takes that database and sql.js library along with a widget code to make that database embeddable in a website such as a content management system
- The whole database for 27 websites we used ended up being just a 476 KB docs.db file that is small to host and use. SQLite does have limits on performance as size grows so this application is definitely more used for small instances and with a lot of sites using an actual SQL database and creating a more in depth search with it is recommended.

# Usage

The first thing is to copy all of the files in this repository to a location where you can run python. If you wish to use your own list of urls and websites, you do not want to copy over the content folder. It is an example of what will be output by harvest.py and if those markdown files are copied they will be added to your database. 

## URLs

You'll need to edit urls.txt to contain the urls of the websites you wish to scrape and search. They need to be in the same format as the text file is currently with the urls contained within quotes and separated by commas: "https://example.html", "https://example2.html"

## Python

First, install all the packages you will need:

```shell
pip install requests bs4 html2text os urllib.parse typing sqlite3 pathlib datetime frontmatter re
```

Double check if you already have a content folder that it is empty, otherwise duplicates or unwanted markdown files may exist there.

Then run:

```shell
python havest.py
```

This will create a content folder if you do not already have one and put the scraped markdown files of the website content there.

Next run:

```shell
python database.py
```

This will create a docs.db file which is the SQLite database containing the information in the markdown files. This docs.db file will need to be copied to wherever the widget is embedded.

## Javascript

You will need all three javascript files hosted somewhere that can be accessed online. The files sql-wasm-dataURL.js and sql-wasm.js are the implementation of SQLite on javascript and do not need to be edited. The file widget.js details the embeddable widget itself and will need to be edited. The main edited spots are marked with //NEED TO CHANGE: and details what needs to be changed for your specific widget. The css-styles and the titles and wording can all also be changed to match your specific project.

## HTML

The file test.html outlines an example of what the embeddable html will look like for your final project. You will need to change the paths to where the javascript files are actually located for your project. 
