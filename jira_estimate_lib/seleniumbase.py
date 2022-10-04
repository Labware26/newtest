# Будем тут записывать наши базовые методы
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from typing import List


class Seleniumbase:
    def __init__(self, driver):
        self.driver = driver
        self.__wait = WebDriverWait(self.driver, 10, 0.3)

    def __get_selenium_by(self, find_by: str):  # find_by -  что найти?
        find_by = find_by.lower()  # переводим значение в нижний регистр
        # если найти надо будет css, то найдем в словаре по ключу и получим нужный метод
        locating = {'css': By.CSS_SELECTOR,
                    'xpath': By.XPATH,
                    'class_name': By.CLASS_NAME,
                    'id': By.ID,
                    'link_text': By.LINK_TEXT,
                    'partial_link_text': By.PARTIAL_LINK_TEXT,
                    'name': By.NAME,
                    'tag_name': By.TAG_NAME}
        return locating[find_by]

    def is_visible(self, find_by: str, locator: str, locator_name: str = None) -> WebElement:
        return self.__wait.until(ec.visibility_of_element_located((self.__get_selenium_by(find_by), locator)), locator_name)

    def is_present(self, find_by: str, locator: str, locator_name: str = None) -> WebElement:
        return self.__wait.until(ec.presence_of_element_located((self.__get_selenium_by(find_by), locator)), locator_name)

    # Иногда нужно дождаться когда элемент пропадет со страницы
    def is_not_present(self, find_by: str, locator: str, locator_name: str = None) -> WebElement:
        return self.__wait.until(ec.invisibility_of_element_located((self.__get_selenium_by(find_by), locator)), locator_name)

    # Функция которая будет реагировать больше чем на один элемент на странице. т.е. если нам нужно найти много элементов на странице
    def are_visible(self, find_by: str, locator: str, locator_name: str = None) -> List[WebElement]:
        return self.__wait.until(ec.visibility_of_all_elements_located((self.__get_selenium_by(find_by), locator)), locator_name)

    def are_present(self, find_by: str, locator: str, locator_name: str = None) -> List[WebElement]:
        return self.__wait.until(ec.presence_of_all_elements_located((self.__get_selenium_by(find_by), locator)), locator_name)

    def get_text_from_webelements(self, elements: List[WebElement]) -> List[str]:
        return [element.text for element in elements]

    #Создадим метод который вернет вебэлемент по его тексту
    def get_element_by_text(self, elements: List[WebElement], name: str) -> WebElement:
        name = name.lower()  #Сразу зададим что наша строка в нижнем регистре
        return [element for element in elements if element.text.lower() == name][0]  # вернем только первый элемент даже если их найдется несколько

    def delete_cookie(self, cookie_name: str) -> None:
        self.driver.delete_cookie(cookie_name)

    def get_find_element(self, find_by: str, locator: str) -> WebElement:
        return self.driver.find_element(self.__get_selenium_by(find_by), locator)
