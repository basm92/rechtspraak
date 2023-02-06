import pandas as pd
import numpy as np
import requests
import re
from bs4 import BeautifulSoup
import locale
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

def convert_money(money_string):
    """
    Convert a Dutch-format money string to a float
    First, delete the dots or comma's at the end of the string
    Then, delete the euro sign and turn into a float
    """
    
    pattern = re.compile(r'[.,]\s*$')
    string = re.sub(pattern, '', money_string)
    out = locale.atof(string.strip().strip('€').strip('\,-')) 
    return out


# helper functions
def extract_text_until(element, stopclass: str):
    """
    In a given node, extract the text until you face an element of a given class.
    In this case, used to extract the names of all plaintiffs and defendants, but nothing more. 
    """
    desired_text = ""
    for current_element in element.find_all():
        if not current_element.has_attr("class"):
            
            desired_text += current_element.text + "\n"
            current_element = current_element.find_next_sibling()
            
            continue
        
        if stopclass in current_element["class"]:
            # Stop the loop if the current element is a div with class "stop"
            break
        
        desired_text += current_element.text + "\n"
        current_element = current_element.find_next_sibling()
        
    return desired_text
