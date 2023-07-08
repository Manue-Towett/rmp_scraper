# RMP Scraper
Scrapes schools from rate my professors

### Requires
python 3.11

### Dependencies
 - Pandas
 - Requests

### Usage
 Configure the follwing project settings in the settings.json file within the settings directory
 - Set the number of threads depending on the processing power of your machine. Only integer values accepted
 - Set the output directory for the scraped data
 - Set the file_path of the csv containing school ids and specify the column name
 - Set the file headers to your liking
 - Set the duplicate rule. Only boolean values allowed i.e. true or false

 command: python3 rmp_scraper.py 
 
 NB. make sure you are in the root project directory {rmp_scraper} before running the command
