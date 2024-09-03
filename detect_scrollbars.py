import argparse
from selenium import webdriver

def main(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    with open('detect_scrollbars.js', 'r') as file:
        script = file.read()

    scrollable_elements = driver.execute_script(script)

    for index, element in enumerate(scrollable_elements, start=1):
        str = f"""Scrollbar {index}: Tag: {element['tag']}, ID: {element['id']}, Classes: {element['classes']}, Link: {url + "#" + element['id']}, ScrollHeight: {element['scrollHeight']},ClientHeight: {element['clientHeight']}"""
        print(str)

    driver.quit()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Detects scrollable elements on a webpage.')
    parser.add_argument('url', type=str, help='webpage URL')
    
    args = parser.parse_args()
    
    main(args.url)