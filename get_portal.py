import argparse
import getpass
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from rcedit_redux import RCEdit

app = Flask(__name__)
scrollable_elements_data = [] 

username = ''
password = ''
session = None  # Global rcedit session
driver = None
expo = None
portal = None


def rc_login(portal, username, password):
    global session, expo
    session = RCEdit()
    session.login(username=username, password=password)
    expo = session.get_portal(portal)
    print(session)
    return session


@app.route('/')
def index():
    global expo
    if expo is None:
        return render_template_string(login_redirect_template)
    return expo
#render_template_string(html_template, elements=scrollable_elements_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        global username, password, portal

        portal = request.form['portal']
        username = request.form['username']
        password = request.form['password']
        
        rc_login(portal, username, password)

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
        <label for="portal">Portal:</label>
        <input type="text" id="portal" name="portal" required><br><br>
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

html_template = expo

if __name__ == '__main__':
    app.run(debug=True)