import time

import pytest
# from selenium import webdriver #Еще раз импортируем веб драйвер что бы использовать методы поиск на странице
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as ec
# from selenium.webdriver.support.ui import WebDriverWait
# from pom.homepage_nav import HomepageNav
from github.pom.homepage_nav import HomepageNav


@pytest.mark.usefixtures('setup')
class TestHome:

    # def test_homepage(self):
    #     driver = webdriver.Chrome()
        # driver.find_element()  # Найдет только один элемент на странице, первый попавшийся
        # driver.find_elements()  # Найдет все элементы
        # driver.find_element(By.CSS_SELECTOR, '#id_123')  # #id_123 как понимаю имя селектора на странице. и он будет искаться. Есил его нет, нам вернется ошибка
        # find_element при поиске не будет ждать пока элемент прогрузиться или еще что то. Поэтому нужно указать драйверу что бы он ждал
        # driver.implicitly_wait(5)  # Будем ждать 5 секунд
        # driver.find_element(By.CSS_SELECTOR, '#id_123')
        # Такой подход не очень хороший, много ожиданий

        # wait = WebDriverWait(driver, 15, 1)  # наш драйвер будет проверять на странице элемент каждые 1 сек, в течении 15 секунд
        # если не прописывать 3 параметр, то частота проверки 0,5 сек

        # element = wait.until(ec.visibility_of_element_located(By.CSS_SELECTOR, '#id_123'))  # until - "подожди до момента пока что то не исполниться"

        # ec.visibility_of_element_located() - виден ли наш элемент на странце
        # Т.е. в нашем примере мы будем ждать пока не будет найден элемент #id_123, по сле чего ec.visibility_of_element_located(By.CSS_SELECTOR, '#id_123') вернет TRUE
        # а wait.until вернет объект ВЕБ ЭЛЕМЕТ
        # driver.find_element(By.CSS_SELECTOR, '#id_123') так же возвращает объект ВЕБ ЭЛЕМЕТ


# Можно запустить из консоли с флагами: pytest -s -v (что то будет показывать если тест провален). Тек же если не
# указать конкретно нужную папку и файл, то pytest найдет папку tests и будет идти по всем тестам в папке.
# Слово test в названии файлов обязателен, если это тесты

#УРОК 2. Напишем базовый класс, который будем потом наследовать в других классах
    def test_nav_links(self):
        homepage_nav = HomepageNav(self.driver)
            #Закоментировано на 5 уроке
            # actual_links = homepage_nav.get_nav_links_text()  # Текущие имена на странице
            # expected_links = homepage_nav.NEW_LINK_TEXT  # Строка имен с которой будем сравнивать
            # assert actual_links == expected_links, 'Валидность навигационных ссылок (текст)'
            # homepage_nav.get_nav_link_by_name('Beauty').click()
        #Закоментировано после поиска нужного куки:
        # cookies = homepage_nav.driver.get_cookies()  # Получвем все кукис стриницы. Что бы это сработало пришлось закоментировать очистку всех кукисов в фикстуре
        # cookies_names = [cookie['name'] for cookie in cookies]
        # print(cookies)
        # print("-------------------------------------------------------------------------------")
        # print(cookies_names)
        # homepage_nav.driver.delete_cookie('ak_bmsc')
        for indx in range(12):
            homepage_nav.get_nav_links()[indx].click()
            # for cookie_name in cookies_names:
            #     homepage_nav.driver.delete_cookie('cookie_name')  #Удаляет одоно куки по имени
            #     print(cookie_name)
            #     homepage_nav.driver.refresh()  #Делаем рефреш страницы
            #     homepage_nav.is_visible('tag_name', 'h1', cookie_name)  # Ищем на странице accec denid по тегу, и укажем на каком куки тег пропал
            # time.sleep(3)
            # homepage_nav.driver.delete_cookie('ak_bmsc')

# Тест запускать pytest -s -v . Но что то не получилось. Пришлось создать пустой файл conftest.py в корне проекта



