from selenium.webdriver.support.events import AbstractEventListener


# https://www.selenium.dev/selenium/docs/api/rb/Selenium/WebDriver/Support/AbstractEventListener.html
# https://www.selenium.dev/selenium/docs/api/py/webdriver_support/selenium.webdriver.support.event_firing_webdriver.html#selenium.webdriver.support.event_firing_webdriver.EventFiringWebDriver
# listener - слушатель


class MyListener(AbstractEventListener):

    def before_click(self, element, driver):
        # Seleniumbase(driver).delete_cookie('ak_bmsc')
        print('before_click')

    def after_click(self, element, driver):
        print('after_click')
        # Seleniumbase(driver).delete_cookie('ak_bmsc')
