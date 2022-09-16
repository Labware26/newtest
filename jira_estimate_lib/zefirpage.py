from time import sleep
from selenium.common import NoSuchElementException
from github.jira_estimate_lib.seleniumbase import Seleniumbase
from selenium.webdriver.remote.webelement import WebElement
from typing import List


class Zefirpage(Seleniumbase):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

        self.__next_link: str = '#pagination-zql-next-page-execution'
        self.__username = '#login-form-username'
        self.__password = '#login-form-password'
        self.__zephyr_zql_switch = '#zephyr-zql-switch>a.switcher-item.active'
        self.__zql_text = '#zqltext'
        self.__tsz = '//tbody/tr/td[3]/a'
        self.__person_name = '//tbody/tr/td[11]/a'


    # Функцию которая должна найти эти все элементы и вернуть
    # def get_nav_links(self) -> List[WebElement]:
    #     return self.are_visible('css', self.__nav_links, 'Header Navigation Links')

    # Функцию которая должна найти элемент и вернуть
    def get_login_form_username(self) -> WebElement:
        return self.is_visible('css', self.__username, 'UserName')

    def get_login_form_password(self) -> WebElement:
        return self.is_visible('css', self.__password, 'Password')

    def get_zephyr_zql_switch(self) -> WebElement:
        return self.is_visible('css', self.__zephyr_zql_switch, 'Zephyr_zql_switch')

    def get_zql_text(self) -> WebElement:
        return self.is_visible('css', self.__zql_text, 'zql_text')

    def get_tsz(self) -> List[WebElement]:
        return self.are_visible('xpath', self.__tsz, 'tsz')

    def get_person_name(self) -> List[WebElement]:
        return self.are_visible('xpath', self.__person_name, 'person_name')

    def get_next_link(self) -> WebElement:
        return self.get_find_element('css', self.__next_link)

    def get_all_issue_list(self) -> List:
        print('Приготовились листать страницы')
        list_rez = []
        while True:
            sleep(0.5)
            num = self.get_text_from_webelements(self.get_tsz())
            person = self.get_text_from_webelements(self.get_person_name())
            print('Прочитали данные')
            for i in range(len(person)):
                list_rez.append([person[i], num[i]])
            try:
                self.get_next_link().click()
                print('Перешли на следующую страницу')
            except NoSuchElementException:
                break
        return list_rez


