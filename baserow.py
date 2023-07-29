import os
import csv
import requests
from baserow.client import BaserowClient
from baserow.orm.database import Database
from baserow.orm.table import Table

# Load environment variables
BASEROW_URL = os.getenv('BASEROW_URL')
BASEROW_TOKEN = os.getenv('BASEROW_TOKEN')
BASEROW_USER = os.getenv('BASEROW_USER')
BASEROW_PASSWORD = os.getenv('BASEROW_PASSWORD')
BASEROW_DB_NAME = os.getenv('BASEROW_DB_NAME')
BASEROW_TABLE_NAME = os.getenv('BASEROW_TABLE_NAME')

# Fetch JWT
response = requests.post(
    f"{BASEROW_SERVER}/api/user/token-auth/",
    data={"username": BASEROW_USER, "password": BASEROW_PASSWORD}
)

if response.status_code == 200:
    data = response.json()
    BASEROW_JWT = data["token"]
else:
    print("Failed to get JWT:", response.content)
    exit(1)

# Initialize Baserow client
client = BaserowClient(BASEROW_SERVER, BASEROW_JWT)

# Connect to a specific Baserow database and table
database = Database(client, id=<DATABASE_ID>)
table = Table(database, id=<TABLE_ID>)

# Read the output CSV file
with open('channel_info.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)  # Skip the header
    for row in reader:
        channel_name = row[0]
        telegram_link = row[1]
        followers = row[2]
        channel_id = row[3]

        # Find matching telegram channel link in the Baserow table
        matching_rows = table.filter(telegram_link=telegram_link)

        if matching_rows:
            # Update the Baserow table with the Channel ID
            for matching_row in matching_rows:
                matching_row.update(channel_id=channel_id)
        else:
            # Update the CSV row with an "absent" field if the telegram link is not in the Baserow table
            row.append('absent')

# Write the updated rows back to the CSV file
with open('channel_info.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(rows)
