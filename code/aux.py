import pandas as pd
import numpy as np
import requests
import re
from bs4 import BeautifulSoup
import locale
import time
locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')

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
    try: 
    	out = locale.atof(string.strip().strip('€').strip('\,-').strip(')').strip('.-;').strip('\u202c').strip(',=')) 
    except:
    	out = 0
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
    
# Extract plaintiffs and defendants
# Find the div with the text "The desired text"

def extract_plaintiffs_and_defendants(soup):
    """
    From a soup-ed html document, extract the defendents and plaintiffs 
    by making use of the fixed HTML structure inside each court case.
    Returns: list of all defendants, plaintiffs, and their respective lawyers
    
    Imports: extract_text_until, bs4.BeautifulSoup
    """
    defs, plntfs, lawyers_defs, lawyers_plntfs = None, None, None, None
    
    # find the text and the plaintiff div
    try:
    	desired_text = soup.find("p", text="in de zaak van").parent.parent
    	# Find the div to which the desired text belongs
    	desired_div = desired_text.find_next_sibling("div")
    	plaintiffs = desired_div
    except:
    	desired_text = soup.find("div", {'class':'uitspraak-info'})
    	plaintiffs = desired_text
    	
    try:
    	desired_text = soup.find(text = lambda text: re.search(r'tegen\:', text)).parent.parent
    	desired_div = desired_text.find_next_sibling("div")
    	defendants = desired_div
    except:
    	desired_text = soup.find(text = lambda text: re.search(r'tegen', text)).parent.parent
    	
    	desired_div = desired_text.find_next_sibling("div")
    	defendants = desired_div
    
    if soup.find_all(text = lambda text: re.search(r'advocaten mrs.|advocaat mr.|gemachtig', text)):
    	lawyers = soup.find_all(text = lambda text: re.search(r'advocaten mrs.|advocaat mr.|gemachtig', text))[:2]
    else: 
    	lawyers = None
    
    return defs, plntfs, lawyers
    
# Bedrag?
## check conventie/reconventie
## loop through variables text instead of text['Het geschil'].iloc[i]
## set operator because otherwise numbers are being mentioned more than once, filter that out

def extract_numbers(geschil):
    """
    From a _geschil_ text, extract the money that is at stake. 
    Differentiate between conventie and reconventie.
    
    Return: set of nos., set of nos (conventie, if applicable), 
    set of nos. (reconventie, if applicable)
    
    Import: convert_money, re
    """
    #geschil = text['Het geschil'].iloc[7]
    unique_numbers, unique_numbers_conventie, unique_numbers_reconventie = None, None, None
    ## if reconventie
    if re.search(r'reconventie', geschil):
        conventie = re.search(r".*reconventie", geschil).group(0)
        reconventie = re.search(r"reconventie.*", geschil).group(0)
    
        raw_conventie = re.findall(r"€ .*?\s", conventie)
        raw_reconventie = re.findall(r"€ .*?\s", reconventie)
    
        unique_numbers_conventie = set([convert_money(x) for x in raw_conventie])
        unique_numbers_reconventie = set([convert_money(x) for x in raw_reconventie])
    
## if no reconventie    
    else: 
        raw_numbers = re.findall(r"€ .*?\s", geschil)
        numbers = [convert_money(x) for x in raw_numbers]
        unique_numbers = set(numbers)
        
    return unique_numbers, unique_numbers_conventie, unique_numbers_reconventie
    
## two different things i can do
## 1. capture reconventie and conventie before splitting
## 2. looking at each point separately and judging then
## I implement 1
## pipeline as follows. Loop through all beslissingen

def extract_uitkomst(beslissing):
    """
    Find indicators regarding the outcome of a trial. 
    Split up within sections and find keywords in each section
    Also extract the money numbers in each of the sections 
    Finally, make use of the conventie-reconventie split up if this is the case
    
    Return: for each section, a spot in: lose, lose_conv, lose_reconv (if applicable)
    money, money_conv, money_reconv (if applicable)
    """
    #beslissing = text['De beslissing'].iloc[325]
    lose = dict()
    lose_conv = dict()
    lose_reconv = dict()
    money = dict()
    money_conv = dict()
    money_reconv = dict()

    if re.search(r'reconventie', beslissing):
        # Split up conventie and reconventie part
        conventie, _, reconventie = beslissing.partition('reconventie')
        ### 2. loop through all clauses to find the numbers involved (conventie)
        clauses = re.split('\d\.\d\.', conventie)
        for i, clause in enumerate(clauses):
            lose_conv[i] = re.search(r"wijst.*vorder.*af|.*niet-ontvankelijk.*", clause)
            bedragen = re.findall(r"€ .*?\s", clause)
            numbers = [convert_money(x) for x in bedragen]
            unique_numbers = set(numbers)
            money_conv[i] = unique_numbers
        ### 3. loop through all clauses to find the numbers involved (reconventie)
        clauses = re.split('\d\.\d\.', reconventie)
        for i, clause in enumerate(clauses):
            lose_reconv[i] = re.search(r"wijst.*vorder.*af|.*niet-ontvankelijk.*", clause)
            bedragen = re.findall(r"€ .*?\s", clause)
            numbers = [convert_money(x) for x in bedragen]
            unique_numbers = set(numbers)
            money_reconv[i] = unique_numbers
               
    else:
        clauses = re.split('\d\.\d\.', beslissing)
        for i, clause in enumerate(clauses):
            ### 3. Within loop, extract the first number after each veroordeling
            lose[i] = re.search(r"wijst.*vorder.*af|.*niet-ontvankelijk.*", clause)
            bedragen = re.findall(r"€ .*?\s", clause)
            numbers = [convert_money(x) for x in bedragen]
            unique_numbers = set(numbers)
            money[i] = unique_numbers

    return lose, lose_conv, lose_reconv, money, money_conv, money_reconv
    

