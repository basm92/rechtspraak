import pandas as pd
import numpy as np
import requests
import re
from bs4 import BeautifulSoup, NavigableString
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
    
# Helper extract_text
def extract_text(element, end, texts):
    if element == end:
        return
    if isinstance(element, NavigableString):
        texts.append(element)
        element = element.next
        extract_text(element, end, texts)
    else:
        element = element.next
        extract_text(element, end, texts)
        
 # Helper for the new soup (inside extract plaintiffs/defendants):
def make_new_soup(node_in_old_soup):
    elements = []
    node = node_in_old_soup

    while node:
    	elements.append(node)
    	node = node.find_next()

    content = ''.join([str(element) for element in elements])
    new_soup = BeautifulSoup(content, 'html.parser') 
    
    return new_soup

# Final helper - delete duplicates from list
def delete_duplicates(lst):
    new_list = []
    for element in lst:
    	if element not in new_list:
    	    new_list.append(element)
    return new_list


# Find the div with the text "The desired text"
def extract_plaintiffs_defendants(soup):
    # For plaintiffs
    start = soup.find(text = lambda text: re.search(r'in de zaak van|in de zaak|inzake|i n z a k e|INZAKE|I N Z A K E', text))
    end = soup.find(text = lambda text: re.search(r'tegen\:', text))
    
    if not end:
        end = soup.find(text = lambda text: re.search(r'tegen', text)) 
    	
    plaintiffs = []
    extract_text(start, end, plaintiffs)

    # Texts for plaintiffs
    plaintiffs = delete_duplicates([text for text in plaintiffs if len(text) > 3])

    # Texts for defendants
    ## Update the soup to only loop for stuff after the plaintiff information
    new_soup = make_new_soup(end)
    new_start = new_soup.find(text = lambda text: re.search(r'tegen', text))
    new_end = new_soup.find(text = lambda text: re.search(r'genoemd|aangeduid|noemen', text))

    if not new_end or len(new_end) > 500:
        new_end = new_soup.find(text = lambda text: re.search(r'procedure|Procedure|PROCEDURE', text)) 
    
    defendants = []
    extract_text(new_start, new_end, defendants)
    defendants = delete_duplicates([text for text in defendants if len(text) > 3])
    
    return plaintiffs, defendants

def extract_lawyers(soup):
    """
    From a soup-ed html document, extract the defendents and plaintiffs 
    by making use of the fixed HTML structure inside each court case.
    Returns: list of all defendants, plaintiffs, and their respective lawyers
    
    Imports: extract_text_until, bs4.BeautifulSoup
    """
    
    # find the text and the plaintiff div
    ## Approach: find the strings "in de zaak van|inzake|i n z a k e|" and "tegen|t e g e n" and extract everything
    ## in between - this is plaintiff
    
    ## Approach: find the strings "tegen" and "genoemd|aangeduid"
    ## in between - this is defendant
    ## if this doesn't work, or if len(text in between) is too long, find everything between tegen and r"procedure|Procedure|PROCEDURE"
    
    ## This part is okay, the above part should be corrected
    if soup.find_all(text = lambda text: re.search(r'advocaten mrs.|advocaat mr.|gemachtig', text)):
    	lawyers = soup.find_all(text = lambda text: re.search(r'advocaten mrs.|advocaat mr.|gemachtig', text))[:2]
    else: 
    	lawyers = None
    
    return lawyers
    
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
    

