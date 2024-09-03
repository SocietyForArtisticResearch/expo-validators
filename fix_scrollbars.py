import argparse
from selenium import webdriver
from rcedit import RCEdit
import getpass

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

def main(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    with open('detect_scrollbars.js', 'r') as file:
        script = file.read()

    scrollable_elements = driver.execute_script(script)
    scrollbars_count = len(scrollable_elements)
    
    for index, element in enumerate(scrollable_elements, start=1):
        str = f"""Scrollbar {index}: Tag: {element['tag']}, ID: {element['id']}, Classes: {element['classes']}, Link: {url + "#" + element['id']}, ScrollHeight: {element['scrollHeight']}, ClientHeight: {element['clientHeight']}"""
        print(str)
    
    if scrollbars_count: 
        print(f"{scrollbars_count} scrollbars found. Login to fix them.")

        username = input('Enter username: ')
        password = getpass.getpass('Enter password: ')
        session = RCEdit(url.split('/')[4])
        session.login(username=username, password=password)

        for index, element in enumerate(scrollable_elements, start=1):
            fix_scrollbar(session, int(element['id'].split('-')[1]), int(element['scrollHeight']))
    else:
        print("No scrollbars found.")

    driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detects scrollable elements on a webpage.')
    parser.add_argument('url', type=str, help='webpage URL')
    
    args = parser.parse_args()
    
    main(args.url)