from recombee_api_client.api_client import *
from recombee_api_client.api_requests import *
from recombee_api_client.exceptions import APIException
import pandas as pd

client = RecombeeClient(
  'my-comp-dev', 
  'vzkvccJzOB1K5bUeprYvBGPjz2FTMQO9zTJ49yd6vAyudDoVOYkct1spVcN1s34E'
)

# Send the name of the properites of the products and their type
client.send(Batch([
  AddItemProperty('Item_Purchased', 'string'),
  AddItemProperty('Category', 'string'),
  AddItemProperty('Size', 'string'),
  AddItemProperty('Color', 'string'),
  AddItemProperty('Season', 'string'),
  AddUserProperty('Gender', 'string')
]))

# Read the .csv file downloaded from here:
# https://www.kaggle.com/datasets/iamsouravbanerjee/customer-shopping-trends-dataset
df = pd.read_csv('shopping_trends.csv')

# Reduce the dataset to the first 1000 entries
df = df.head(1000)

for index, row in df.iterrows():

    # Generate unique id for each item
    item_id = f"{row['Item Purchased']}-{row['Category']}-{row['Size']}-{row['Color']}-{row['Season']}"
    
    # Check if the item was already added in the database
    try:
        client.send(AddItem(item_id))
    except APIException as e:
        print(f"Item {item_id} already exists. Skipping request.")

    # Send the values of the properties added for each item
    # and the user who made that particular purchase,
    # then associate the values
    client.send(Batch([
      SetItemValues(
          item_id,
          {
              'Item_Purchased': row['Item Purchased'],
              'Category': row['Category'], 
              'Size': row['Size'],
              'Color': row['Color'],
              'Season': row['Season']
          }, 
          cascade_create=True
      ),
      AddUser(row['Customer ID']),
      SetUserValues(
          row['Customer ID'],
          {
              'Gender': row['Gender']
          },
          cascade_create=True
      ),
      AddPurchase(row['Customer ID'], item_id)
    ]))

# For the first 150 users, recommend 3 items from the database
for user_id in df['Customer ID'].unique().tolist()[:150]: 
    recommended = client.send(RecommendItemsToUser(user_id, 3))
    print(recommended)
