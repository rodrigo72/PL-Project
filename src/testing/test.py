from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

import xml.etree.ElementTree as ET
import subprocess

COMPILE_TIMEOUT = 3
PAGE_LOAD_TIMEOUT = 1


def get_result(code):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://ewvm.epl.di.uminho.pt/run')

    time.sleep(PAGE_LOAD_TIMEOUT)
    textarea = driver.find_elements(By.NAME, "code")[0]
    textarea.send_keys(code)

    run_input = driver.find_element(By.XPATH, "/html/body/div/div[1]/div[1]/form/div[2]/div[2]/input[2]")
    run_input.click()
    time.sleep(COMPILE_TIMEOUT)
    result = driver.find_elements(By.XPATH, '/html/body/div/div[1]/div[2]/form/div/div/span')[0].text
    
    driver.quit()
    return result


def main():
    tree = ET.parse("tests.xml")
    root = tree.getroot()
    
    tests = []
    for test in root.findall('test'):
        tests.append({
            "name": test.find("name").text.strip(),
            "input": test.find("input").text.strip(),
            "output": test.find("output").text.strip(),
            "result": None
        })  
    
    for test in tests:
        forth_yacc = subprocess.run(["python3", "forth_yacc.py", test['input']], capture_output=True, text=True, cwd="../")
        ewvm_code = forth_yacc.stdout.strip()
        result = get_result(ewvm_code)
        test['result'] = result
        
    for test in tests:
        print(f"Test: {test['name']}")
        print(f"Expected: {test['output']}")
        print(f"Result: {test['result']}")
        print()
        assert test['output'].strip() == test['result'].strip()
    

if __name__ == '__main__':
    main()