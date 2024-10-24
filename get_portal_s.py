import argparse
import getpass
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from rcedit_redux import RCEdit
from rc_soup_pages import getAllPages
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
scrollable_elements_data = [] 

username = ''
password = ''
session = None  # Global rcedit session
driver = None
expo = None
portal = None

session = RCEdit()
session.login(username='scrollboy@gmail.com', password='scrollboy')
print(session)
portal = session.get_portal(6)

print(portal)