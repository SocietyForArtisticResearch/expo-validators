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

    def __init__(self, exposition):
        self.session = requests.Session()
        self.exposition = exposition


    def login(self, username, password):
        rtext = self._post("/session/login", data=dict(username=username, password=password))
        if rtext.strip():
            raise RCException("login failed")


    def logout(self):
        self._get("/session/logout")


    def item_list(self, page_id, item_name=None, item_type=None, firstonly=False, regexp=False):
        "List items on page (aka weave), optionally filtered"
        rtext = self._post("/editor/content", data=dict(research=self.exposition, weave=page_id))
        items = self._ItemLister()(rtext)

        if item_name is None:
            critn = lambda n: True
        else:
            if regexp:
                r = re.compile(item_name)
                critn = lambda n: r.match(n) is not None
            else:
                critn = lambda n: n == item_name

        if item_type is None:
            critt = lambda t: True
        else:
            critt = lambda t: t == item_type
                
        items = [(itid,(ittp,itnm)) for itid,(ittp,itnm) in items.items() if critn(itnm) and critt(ittp)]
            
        if firstonly:
            return items[0] if len(items) else None
        else:
            return dict(items)

    #updated to API september 2024
    def item_update(self, item_id, x, y, w, h, r=0):
        "Fast item positioning update"
        data = {
            'research': self.exposition,
            "resize": "true",
            #f'item[{item_id}]': item_id,
            f'data[{item_id}][left]': x,
            f'data[{item_id}][top]': y,
            f'data[{item_id}][width]': w,
            f'data[{item_id}][height]': h,
            f'data[{item_id}][rotate]': r,
        }
        rtext = self._post('/item/update', data=data)
        #if rtext.strip():
        #    raise RCException("item_update failed")


    def item_get(self, item_id):
        rtext = self._get("/item/edit", params=dict(research=self.exposition, item=item_id))
        return self._ItemData()(rtext)
    

    def item_remove(self, item_id):
        "Remove item from page (aka weave)"
        rtext = self._post("/item/remove", data={'research': self.exposition, 'item[]': item_id, 'confirmation': 'confirmation'})
        if rtext.strip():
            raise RCException("item_remove failed")


    #### internal methods #####################################################

    class _PageLister(HTMLParser):
        def __call__(self, html):
            self.items = {}
            self.nest_tr = 0
            self.feed(html)
            return self.items

        def handle_starttag(self, tag, attrs):
            if tag == 'tr':
                self.nest_tr += 1
                if self.nest_tr == 1:
                    self.nest_td = 0
                    self.cnt_td = 0
                    attrs = dict(attrs)
                    try:
                        self.item = attrs['data-id']
                    except:
                        pass
            elif tag == 'td' and self.nest_tr == 1:
                self.nest_td += 1
                self.cnt_td += 1

        def handle_endtag(self, tag):
            if tag == 'tr':
                self.nest_tr -= 1
            elif tag == 'td' and self.nest_tr == 1:
                self.nest_td -= 1

        def handle_data(self, data):
            if self.nest_tr == 1:
                pos = (self.nest_td, self.cnt_td)
                # pos == (1,1): type (graphical, block, iframe)
                # pos == (1,2): title
                # pos == (1,3): date
                if pos == (1,2):
                    self.items[self.item] = data


    class _SetLister(HTMLParser):
        def __call__(self, html):
            self.items = {}
            self.nest_tr = 0
            self.feed(html)
            return self.items

        def handle_starttag(self, tag, attrs):
            if tag == 'tr':
                self.nest_tr += 1
                if self.nest_tr == 1:
                    self.nest_td = 0
                    self.cnt_td = 0
                    attrs = dict(attrs)
                    try:
                        if attrs['class'] == 'work':
                            self.item = attrs['data-id']
                    except:
                        pass
            elif tag == 'td' and self.nest_tr == 1:
                self.nest_td += 1
                self.cnt_td += 1

        def handle_endtag(self, tag):
            if tag == 'tr':
                self.nest_tr -= 1
            elif tag == 'td' and self.nest_tr == 1:
                self.nest_td -= 1

        def handle_data(self, data):
            if self.nest_tr == 1 and self.nest_td == 1 and self.cnt_td == 2:
                self.items[self.item] = data


    class _SimpleMediaLister(HTMLParser):
        def __call__(self, html):
            self.items = {}
            self.nest_tr = 0
            self.feed(html)
            return self.items

        def handle_starttag(self, tag, attrs):
            if tag == 'tr':
                self.nest_tr += 1
                if self.nest_tr == 1:
                    self.nest_td = 0
                    self.cnt_td = 0
                    attrs = dict(attrs)
#                    print(tag, attrs)
                    try:
                        if 'simple-media' in attrs['class'].split():
                            self.item = attrs['data-id']
                            self.tool = attrs['data-tool']
                    except:
                        pass
            elif tag == 'td' and self.nest_tr == 1:
                self.nest_td += 1
                self.cnt_td += 1

        def handle_endtag(self, tag):
            if tag == 'tr':
                self.nest_tr -= 1
            elif tag == 'td' and self.nest_tr == 1:
                self.nest_td -= 1

        def handle_data(self, data):
            if self.nest_tr == 1 and self.nest_td == 1 and self.cnt_td == 2:
                self.items[self.item] = (self.tool, data)


    class _ItemLister(HTMLParser):
        def __call__(self, html):
            self.items = {}
            self.feed(html)
            return self.items

        def handle_starttag(self, tag, attrs):
            if tag == 'div':
                attrs = dict(attrs)
                try:
                    self.items[attrs['data-id']] = (attrs['data-tool'], attrs['data-title'])
                except:
                    pass


    class _ItemData(HTMLParser):
        toolmatch = re.compile(r'edit\s*([^\s]+)\s*tool')
        bracketmatch = re.compile(r'([^\[]+)\[([^\]]+)\]')
        
        def __call__(self, html):
            self.title = None
            self.data = defaultdict(dict)
            self.select = None
            self.textarea = None
            self.feed(html)
            return self.title, self.data

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag =='form':
                try:
                    m = self.toolmatch.match(attrs['title'])
                except KeyError:
                    m = None
                if m is not None:
                    self.title = m.group(1)
            elif tag == 'input':  
                tp = attrs.get('type', 'text')
                m = self.bracketmatch.match(attrs['name'])
                v = None
                if m is not None:
                    if tp != 'checkbox' or "checked" in attrs:
                        v = attrs['value']
                if v is not None:
                    self.data[m.group(1)][m.group(2)] = v
            elif tag == 'select':
                m = self.bracketmatch.match(attrs['name'])
                if m is not None:
                    self.select = (m.group(1),m.group(2))
            elif tag == 'option' and self.select is not None:
                if 'selected' in attrs:
                    self.data[self.select[0]][self.select[1]] = attrs['value']
            elif tag == 'textarea':
                m = self.bracketmatch.match(attrs['name'])
                if m is not None:
                    self.textarea = (m.group(1),m.group(2))
            
        def handle_data(self, data):
            if self.textarea is not None:
                self.data[self.textarea[0]][self.textarea[1]] = data
            
        def handle_endtag(self, tag):
            if tag == 'select':
                self.select = None
            elif tag == 'textarea':
                self.textarea = None


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
