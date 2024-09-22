import argparse
import getpass
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rcedit import RCEdit
from rc_soup_pages import getAllPages
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
scrollable_elements_data = [] 

username = ''
password = ''
session = None  # Global rcedit session
driver = None


def rc_login(url, username, password):
    global session
    session = RCEdit(url.split('/')[4])
    session.login(username=username, password=password)
    return session


def detect_scrollbars(driver, url):
    driver.get(url)
    with open('detect_scrollbars.js', 'r') as file:
        script = file.read()
    scrollable_elements = driver.execute_script(script)
    return scrollable_elements


def collect_scrollbars_data(driver, pages):
    global scrollable_elements_data
    scrollable_elements_data = []
    for page_url in pages:
        elements = detect_scrollbars(driver, page_url)
        for element in elements:
            scrollable_elements_data.append({
                'url': page_url,
                'id': element['id'],
                'scrollHeight': element['scrollHeight'],
                'clientHeight': element['clientHeight']
            })


@app.route('/')
def index():
    if session is None:
        return render_template_string(login_redirect_template)
    return render_template_string(html_template, elements=scrollable_elements_data)



@app.route('/fix', methods=['POST'])
def fix_scrollbar_route():
    element_id = request.form['element_id']
    new_height = request.form['new_height']
    fix_scrollbar(session, int(element_id.split('-')[1]), int(new_height))

    return jsonify({'status': 'success', 'message': 'Scrollbar fixed!'})


def fix_scrollbar(session, item, newHeight):
    print(f"{session}, tool: {item}")
    i = session.item_get(item)
    
    session.item_update(
        item, 
        i[1]['style']['left'], 
        i[1]['style']['top'], 
        i[1]['style']['width'], 
        newHeight, 
        i[1]['style']['rotate']
    )


@app.route('/refresh', methods=['POST'])
def refresh_scrollbars_route():
    url = request.form['url']
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    global driver
    driver = webdriver.Chrome(options=options)
    
    expo = requests.get(url)
    parsed = BeautifulSoup(expo.content, 'html.parser')
    pages = getAllPages(url, parsed)

    collect_scrollbars_data(driver, pages)
    driver.quit()

    return jsonify({'status': 'success', 'elements': scrollable_elements_data})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        global username, password, driver

        username = request.form['username']
        password = request.form['password']
        url = request.form['url']
        
        rc_login(url, username, password)
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        
        expo = requests.get(url)
        parsed = BeautifulSoup(expo.content, 'html.parser')
        pages = getAllPages(url, parsed)

        collect_scrollbars_data(driver, pages)
        driver.quit()

        return redirect(url_for('index'))
    return render_template_string(login_template)


login_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
</head>
<body>
    <h1>Login</h1>
    <form action="/login" method="post">
        <label for="url">Exposition URL:</label>
        <input type="text" id="url" name="url" required><br><br>
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required><br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required><br><br>
        <button type="submit">Login</button>
    </form>
</body>
</html>
'''

login_redirect_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scrollable Elements</title>
</head>
<body>
    <h1>Scrollable Elements</h1>
    <p>You need to log in to view the scrollable elements.</p>
    <a href="/login">Login Here</a>
</body>
</html>
'''

html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scrollable Elements</title>
    <style>
        .card {
            border: 1px solid #ccc;
            padding: 16px;
            margin: 16px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: relative;
        }
        .fixed-message {
            margin-top: 10px;
            color: green;
        }
    </style>
    <script>
        function fixScrollbar(event, form) {
            event.preventDefault();
            const formData = new FormData(form);
            fetch('/fix', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const messageElement = document.createElement('div');
                    messageElement.className = 'fixed-message';
                    messageElement.textContent = data.message;
                    form.appendChild(messageElement);
                }
            });
        }

        function refreshScrollbars() {
            const url = '{{ elements[0].url if elements else '' }}';
            const formData = new FormData();
            formData.append('url', url);

            fetch('/refresh', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const container = document.querySelector('body > div');
                    container.innerHTML = '';
                    data.elements.forEach(element => {
                        const card = document.createElement('div');
                        card.className = 'card';
                        card.innerHTML = `
                            <p><strong>URL:</strong> <a href="${element.url}" target="_blank">${element.url}</a></p>
                            <p><strong>ID:</strong> ${element.id}</p>
                            <p><strong>ScrollHeight:</strong> ${element.scrollHeight}</p>
                            <p><strong>ClientHeight:</strong> ${element.clientHeight}</p>
                            <form onsubmit="fixScrollbar(event, this)">
                                <input type="hidden" name="element_id" value="${element.id}">
                                <label for="new_height">New Height:</label>
                                <input type="text" name="new_height" id="new_height" required>
                                <button type="submit">Fix Scrollbar</button>
                            </form>
                        `;
                        container.appendChild(card);
                    });
                }
            });
        }
    </script>
</head>
<body>
    <h1>Scrollable Elements</h1>
    <button onclick="refreshScrollbars()">Refresh Scrollbars</button>
    <div>
        {% if elements and elements|length > 0 %}
            {% for element in elements %}
            <div class="card">
                <p><strong>URL:</strong> <a href="{{ element.url }}" target="_blank">{{ element.url }}</a></p>
                <p><strong>ID:</strong> {{ element.id }}</p>
                <p><strong>ScrollHeight:</strong> {{ element.scrollHeight }}</p>
                <p><strong>ClientHeight:</strong> {{ element.clientHeight }}</p>
                <form onsubmit="fixScrollbar(event, this)">
                    <input type="hidden" name="element_id" value="{{ element.id }}">
                    <label for="new_height">New Height:</label>
                    <input type="text" name="new_height" id="new_height" required>
                    <button type="submit">Fix Scrollbar</button>
                </form>
            </div>
            {% endfor %}
        {% else %}
            <p>No scrollable elements found.</p>
        {% endif %}
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)