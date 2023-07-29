import os
import csv
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

# Initialize Baserow client
client = BaserowClient(BASEROW_URL, BASEROW_TOKEN)

# Authenticate
client.authenticate(BASEROW_USER, BASEROW_PASSWORD)

# Get the database and table
database = Database.get_by_name(client, BASEROW_DB_NAME)
table = Table.get_by_name(database, BASEROW_TABLE_NAME)

# Read the CSV file
with open('telegram_channels.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Find the matching row in the Baserow table
        baserow_row = table.get_row(filter={'telegram_link': row['telegram_link']})

        if baserow_row is not None:
            # Update the row with the Channel ID from the CSV file
            baserow_row.update({'channel_id': row['channel_id']})
        else:
            # Update the CSV row with an "absent" field
            row['absent'] = 'absent'
