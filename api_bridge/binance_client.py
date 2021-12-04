import sys,os
#Add Indicators.py to file's sys.path, to be importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR, junk = BASE_DIR.split("\Code")
lib_path = f"{BASE_DIR}\Code"
sys.path.append(lib_path)
# print("LIB PATH: ",lib_path)
import requests
from binance.client import Client
import ccxt
import sqlite3
import socket
from custom_errors.errors import NetworkError
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# Fixes SSL regulation
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from settings import API_KEY,API_SECRET


proxies = {
    'http': 'http://10.10.1.10:3128',
    'https': 'http://10.10.1.10:1080'
}

# api_key = ""-Connect to server and retreive users credentials
# api_secret = ""--Connect to server and retreive users credentials



try:
    client = Client(API_KEY,API_SECRET,{
        "verify": False,
        "timeout": 20
        })
except requests.exceptions.ConnectionError:
    raise NetworkError("Device needs to  be connected to the internet.")












