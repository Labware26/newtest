import time
from typing import Tuple

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from github.jira_estimate_lib.utils import Utils
from github.jira_estimate_lib.zefirpage import Zefirpage


class Cases:
    def __init__(self):
        self.driver = self.__get_webdriver(self.__get_chrome_options())

    def __get_chrome_options(self):
        options = Options()
        # options.add_argument('chrome')
        # options.add_argument('--start-maximized')
        options.add_argument("--window-size=1920,1080")
        # options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        return options

    def __get_webdriver(self, get_chrome_options):
        options = get_chrome_options
        service = Service(r'chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def completed_cases(self, date: Tuple[str, str]) -> dict:
        url = 'http://192.168.100.230:8080/secure/enav/#?query=project%20%3D%20TSZ%20AND%20executionDate%20%3E%3D' \
              '%202022-09-01%20AND%20executionDate%20%3C%3D%202022-09-30%20AND%20executionStatus%20%3D%20%D0%9F%D0%A0' \
              '%D0%9E%D0%99%D0%94%D0%95%D0%9D&view=list&searchType=basic '
        self.driver.get(url)
        print('webdriver initialization')
        zefir_nav = Zefirpage(self.driver)
        zefir_nav.get_login_form_username().send_keys('aquarius')
        zefir_nav.get_login_form_password().send_keys('buhjr020287e', Keys.RETURN)
        print('Авторизовались в Зефире')
        time.sleep(1)
        zefir_nav.get_zephyr_zql_switch().click()
        print('Переключили поиск на расширенный')
        zefir_nav.get_zql_text().send_keys('project = TSZ AND executionDate >= ' + date[0] + ' AND executionDate <= ' + date[1] + ' AND executionStatus = ПРОЙДЕН', Keys.RETURN)
        print('Произвели поиск')
        list_rez = zefir_nav.get_all_issue_list()
        dict_rez = Utils.get_dict_by_list(list_rez)

        print('\nКол-во пройденных тестов:')
        for i in dict_rez.keys():
            print(i, len(dict_rez[i]))
        self.driver.quit()
        return dict_rez


