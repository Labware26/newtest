from github.jira_estimate_lib.seleniumbase import Seleniumbase
from selenium.webdriver.remote.webelement import WebElement
from typing import List
from github.jira_estimate_lib.utils import Utils


class HomepageNav(Seleniumbase):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.NEW_LINK_TEXT = 'Women,Men,Kids,Home,Beauty,Shoes,Handbags,Jewelry,Furniture,Toys,Gifts,Trending,Sale'

#На странице сайта в режиме просмотра кода, находим класс элемента через поиск
#  #mainNavigationFobs>li    - это будет css локатор
#
        self.__nav_links: str = '#mainNavigationFobs>li'
        #дальше напишем функцию которая должна найти эти все элементы и вернуть

    def get_nav_links(self) -> List[WebElement]:
        return self.are_visible('css', self.__nav_links, 'Header Navigation Links')
    # Мы вернули веб элементы, но нам нужно вернуть текст с этих веб элементов

    def get_nav_links_text(self) -> str:
        # если бы элемент был один, то можно было бы применить к нему метод text - element.text, но так как у нас
        # список элементов, то их из списка надо вернуть

# Упустили один момент, def get_nav_links(self) - возвращает один элемент, а должен список. Для этого импортируем
# from typing import List, и прописываем  -> List[WebElement]: , в базовок классе делаем тоже самое.
        nav_links = self.get_nav_links()
        # Нам нужно поместить все тексты в новый список, из которого потом создать строку
        # nav_links_text = [link.text for link in nav_links]  #метод текс вернет текс веб элемента/ Тут был рефакторинг кода
        nav_links_text = self.get_text_from_webelements(nav_links)
        # return ','.join(nav_links_text)  # Это строку тоже рефакторингуем. Создадим новый класс, так как переводить в строки список будем и дельше
        return Utils.join_strings(nav_links_text)

    #Создадим метод который будет возвращать веб элемент по имени
    def get_nav_link_by_name(self, name: str) -> WebElement:
        elements = self.get_nav_links()
        return self.get_element_by_text(elements, name)

