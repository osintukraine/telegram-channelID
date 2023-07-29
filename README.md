# telegram-channelID
- a python script to retrieve subscribed channel ID's from your telegram account and export the list to CSV
- retrieve the channel ID's from a local CSV file with missing channel ID's


# How to use : 

- python3 -m venv /path/to/this/repo
- source bin/activate
- pip install -r requirements.txt
- cp env-example to .env
- add your app id and api details, phone number
- run : python3 channels.py --mode fetch to fetch the account subscribed channels and their ID
- add phone number and confirm code to create you session file
- wait for the code to finish the job (it can take a while if you have many channels)
- you should end up with a CSV file of all your subscribed channels ID's

## load a local CSV file with missing ID's
- run : python3 channels.py --mode parse --input_file input.csv
