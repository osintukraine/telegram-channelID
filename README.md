# Get Telegram Chat-ID
- a python script to retrieve subscribed channel ID's from your telegram account and export the list to CSV
- retrieve the channel ID's from a local CSV file with missing channel ID's
- infer chat-id's from a OPML list of telegram channels

## TLDR

- python channels.py --mode fetch --output_file output_fetch.csv
- python channels.py --mode parse --input_file input.csv --output_file output_parsed.csv
- python channels.py --mode opml --input_file URL-to-OPML --output_file output.csv



# How to install : 

- python3 -m venv /path/to/this/repo
- source bin/activate
- pip install -r requirements.txt
- cp env-example to .env
- add your app id and api details, phone number to .env
- run : 'python channels.py --mode fetch --output_file output_fetch.csv' to fetch the account subscribed channels and their ID
- confirm phone number and input code to create you session file
- wait for the code to finish the job (it can take a while if you have many channels)
- you should end up with a CSV file of all your subscribed channels ID's

## load a local CSV file with missing ID's
- run : python channels.py --mode parse --input_file input.csv --output_file output_parse.csv
- your CSV file must contain at least a column with Channel_Link
- if Channel_Name is also present the script will use it to infer the Chat ID, if not, it will use the Channel_link. 

## OPML use case mode
this usecase is designed for a very specific situation, the use of Inoreader to aggregate Telegram channels
on this usecase, the user end up with a folder from witch an OPML link can be used to extract Chat ID's from each telegram channel link. 
for this to work, the user need to enable the RSS output for this folder property and then use the Inoreader provided OPML link as input source. 

- python channels.py --mode opml --input_file https://www.inoreader.com/reader/subscriptions/export/user/1005520529/label/Telegram-ampukr --output_file output.csv

the result will be a CSV file with the Telegram Channel Name, Link and Chat ID. 


