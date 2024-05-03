from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

import subprocess
import yaml

COMPILE_TIMEOUT = 2
PAGE_LOAD_TIMEOUT = 1

chrome_options = Options()
prefs = {"profile.managed_default_content_settings.images": 2,
         "profile.default_content_settings.cookies": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://ewvm.epl.di.uminho.pt/run')

time.sleep(PAGE_LOAD_TIMEOUT)

def get_result(code: str) -> str:
    textarea = driver.find_elements(By.NAME, "code")
    if not textarea:
        return "ERROR: textarea not found"
    textarea = textarea[0]
    textarea.clear()
    textarea.send_keys(code)
    
    run_input = driver.find_element(By.XPATH, "/html/body/div/div[1]/div[1]/form/div[2]/div[2]/input[2]")
    run_input.click()
    time.sleep(COMPILE_TIMEOUT)
        
    result = driver.find_elements(By.XPATH, '/html/body/div/div[1]/div[2]/form/div/div/span')
    result_str = ''.join([r.text if r.text != "" else '\n' for r in result])
        
    return result_str


def test(tests, test_name=None, show_input=False):
    
    print()
    for test in tests:
        if not test['test']: 
            continue
        
        if test_name is not None and test_name != test['name']:
            continue
        
        print(f"> {test['name']} : STARTED")
        
        subprocess.run(["python3", "forth_yacc_v2.py", test['input']], cwd="../", check=True)
        with open("../output.txt", "r") as output_file:
            ewvm_code = output_file.read()
        result = get_result(ewvm_code)
        test['result'] = result
        print(f"> {test['name']} : DONE")
        
    print('\n')

    succeded = 0
    failed = 0
    for test in tests:
        if not test['test']: 
            continue
        
        if test_name is not None and test_name != test['name']:
            continue
        
        print('\t-----------------------------')
        print(f"\t{test['name']}\n")
        
        if show_input:
            input_str = '\t' + test['input'].strip().replace('\n', '\n\t')
            print(f"\t::Input::\n{input_str}\n")
        
        output_str = '\n\t' + str(test['output']).strip().replace('\n', '\n\t')
        print(f"\t::Expected:: {output_str}\n")
        
        result_str = '\n\t' + str(test['result']).strip().replace('\n', '\n\t')
        print(f"\t::Result:: {result_str}")
        
        if str(test['output']).strip() == str(test['result']).strip():
            succeded += 1
            print("\t----------SUCCEEDED----------")
        else:
            failed += 1
            print(f"\t------------FAILED------------")
        print('\n')
        
    print()
    print(f"Succeded: {succeded}")
    print(f"Failed: {failed}")
        

def main():
    with open("tests.yaml", "r") as f:
        yaml_data = yaml.safe_load(f)

    tests = yaml_data['tests']
    # test(tests, test_name="depth 1", show_input=True)
    test(tests, show_input=True)
    
    driver.quit()


if __name__ == '__main__':
    print("NO LONGER WORKING DUE TO CHANGES IN THE EWVM WEBSITE")
    # main()
