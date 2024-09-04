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
        str = f"""Scrollbar {index}: ID: {element['id']}, Link: {url + "#" + element['id']}, ScrollHeight: {element['scrollHeight']}, ClientHeight: {element['clientHeight']}"""
        print(str)
    
    if scrollbars_count: 
        print(f"{scrollbars_count} scrollbars found. Login to fix them.")

        username = input('Enter username: ')
        password = getpass.getpass('Enter password: ')
        session = RCEdit(url.split('/')[4])
        session.login(username=username, password=password)

        choice = input("Enter 'A' to fix all scrollbars, or 'S' to select specific scrollbars: ").strip().upper()

        if choice == 'A':
            for index, element in enumerate(scrollable_elements, start=1):
                fix_scrollbar(session, int(element['id'].split('-')[1]), int(element['scrollHeight']))
        elif choice == 'S':
            selected_indices = input("Enter the index of the scrollbars you want to fix (e.g., 1, 3, 5): ")
            selected_indices = [int(x.strip()) for x in selected_indices.split(',') if x.strip().isdigit()]
            
            for index in selected_indices:
                if 1 <= index <= scrollbars_count:
                    element = scrollable_elements[index - 1]
                    fix_scrollbar(session, int(element['id'].split('-')[1]), int(element['scrollHeight']))
                else:
                    print(f"Invalid scrollbar index: {index}")
        else:
            print("Invalid choice. No scrollbars were fixed.")
    else:
        print("No scrollbars found.")

    driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detects scrollable elements on a webpage.')
    parser.add_argument('url', type=str, help='webpage URL')
    
    args = parser.parse_args()
    
    main(args.url)