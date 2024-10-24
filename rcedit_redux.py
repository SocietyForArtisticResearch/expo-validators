# rcedit – programmatic access to Research catalogue web interface
# (c)2021 grrrr.org

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__all__ = ['RCException', 'RCEdit']

import requests
import re
import urllib
from html.parser import HTMLParser
import json
import time
from collections import defaultdict


class RCException(Exception):
    def __init__(self, reason=""):
        self.reason = reason
    def __repr__(self):
        return f'RCException("{self.reason}")'


class RCEdit:
    rcurl = "https://www.researchcatalogue.net"

    def __init__(self):
        self.session = requests.Session()


    def login(self, username, password):
        rtext = self._post("/session/login", data=dict(username=username, password=password))
        if rtext.strip():
            raise RCException("login failed")


    def logout(self):
        self._get("/session/logout")

    def get_portal(self, idx):
        expos = self._get("/portal/search-result?fulltext=&title=&autocomplete=&keyword=&portal=" + str(idx) + "&statusprogress=0&statuspublished=0&includelimited=0&includelimited=1&includeprivate=0&type_research=research&resulttype=research&modifiedafter=&modifiedbefore=&format=json&limit=250&page=0")
        
        return expos

    #### internal methods #####################################################


    def _post(self, url, data=None, files=None, headers=None):
        r = self.session.post(f"{self.rcurl}{url}", data=data, files=files, headers=headers)
        self.last_response = r
        if r.status_code != 200:
            raise RCException(f'POST {url} failed with status code {r.status_code}')
        return r.text


    def _get(self, url, params=None):
        r = self.session.get(f"{self.rcurl}{url}", params=params)
        self.last_response = r
        if r.status_code != 200:
            raise RCException(f'GET {url} failed with status code {r.status_code}')
        return r.text
