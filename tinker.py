import os
from dotenv import load_dotenv
import ipinfo
import pprint
access_token = os.getenv('IPINFO_TOKEN')
handler = ipinfo.getHandler(access_token)
details = handler.getDetails()
pprint.pprint(details.all)