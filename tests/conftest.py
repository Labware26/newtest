import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chrome_options
from selenium.webdriver.chrome.service import Service as chrome_service  #теперь указание пути к драйверу будет идти через service
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from github.abstract.selenium_listener import MyListener
# https://docs.pytest.org/en/6.2.x/fixture.html

# Создаем фикстуру



@pytest.fixture
def get_chrome_options():
    options = chrome_options()
    # Параметры:
    # --headless -Run in headless mode, i.e., without a UI or display server dependencies
    # Запускает тест без отображения интерфейса браузера
    # --start-maximized 	Starts the browser maximized, regardless of any previous settings.
    # окно будет открыто на весь экран
    # --window-size  -Sets the initial window size. Provided as string in the format "800,600".
    # если нам нужен тест с окном определенного размера, то можем использовать данный параметр

    options.add_argument('chrome')  # Данный параметр будем использовать что бы работать с интерфейсом, потом пропишем headless
    options.add_argument('--start-maximized')
    # options.add_argument('--window-size=800,600')
    # https://peter.sh/experiments/chromium-command-line-switches/
    return options


# Далее создаем фикстуру которая будет инициализировать наш драйвер
@pytest.fixture
def get_webdriver(get_chrome_options):
    options = get_chrome_options
    service = chrome_service(r'D:\PythonProj\ProjectPY\new\github\chromedriver.exe') # Задаем Service с путем к драйверу
    # driver = webdriver.Chrome(executable_path=r'D:\PythonProj\ProjectPY\new\github\chromedriver.exe', options=options)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# Создаем фикстуру setup. Что мы будем делать с самого начала. С чего начнется тест
@pytest.fixture(scope='function')
# scope это то как наши тесты будут реагировать на данную фикстуру, то есть она будет использоваться при каждом тесте отдельно,
# каждый наш тест будет запускаться как чистый браузер и в нем будут исполняться какие то действия
# если бы scope='session', то все бы происходило в сессии всего браузера
def setup(request, get_webdriver):  # request - встроенная фикстура которая есть в pytest
    driver = get_webdriver
    driver = EventFiringWebDriver(driver, MyListener())
    # Что будем тестить?
    url = 'http://192.168.100.230:8080/secure/enav/#?query=project%20%3D%20TSZ%20AND%20executionDate%20%3E%3D%202022-09-01%20AND%20executionDate%20%3C%3D%202022-09-30%20AND%20executionStatus%20%3D%20%D0%9F%D0%A0%D0%9E%D0%99%D0%94%D0%95%D0%9D&view=list&searchType=basic'
    # request посмотрит не являются ли наши тесты в классе
    if request.cls is not None:  # Будет ли это класс и если это класс, то
        request.cls.driver = driver
    # А если нет, то есть тесты не в классе, то

    driver.get(url) # метод get откроет наш url
    # driver.delete_all_cookies()  #Этот метод удаляет все куки браузера, так как нас не хотела пускать защита от роботов
    yield driver  # Возвращаем наш драйвер
    # После окончания теста, мы должны закрыть страничку. Если открыто несколько окон, то закроет то, где мы работаем
    # driver.close()
    # Но мы будем использовать другой метод
    driver.quit()  # он полностью закроен наш браузер