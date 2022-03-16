from console import console
import properties as p
import webdriver as web
from sii import SII 
from discord import Discord
from general_utils import Utils

from rich.markdown import Markdown
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import ElementClickInterceptedException

from typing import List, Dict
from abc import ABC, abstractmethod
import os
from dataclasses import dataclass, field
from datetime import datetime
import time
import pytz
chileanTZ = pytz.timezone('America/Santiago')
import random

def main():
    booking = {
        "check_in": "12-11-2021", # B
        "check_out": "14-11-2021", # C
        "name": "Franco Schiappacasse", # E
        "email": "fschiappacassem@gmail.com", # F
        "total_payment_amount": 636438,  # T -> Total amount recieved
    }
# Booking(check_in="12-11-2021", check_out="14-11-2021", 
#   name="Franco Schiappacasse", email="fschiappacassem@gmail.com", 
#   total_payment_amount=636438
#   )


if __name__ == '__main__':
    pass

