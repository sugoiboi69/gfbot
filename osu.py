from ossapi import *
from dotenv import load_dotenv
import os
load_dotenv()

client_secret = os.getenv('OSU_TOKEN')
client_id = os.getenv('OSU_CLIENT')
api = OssapiV2(client_id, client_secret)

#functions
info = api.user(api.search(query="chaser01").users.data[0].id)

