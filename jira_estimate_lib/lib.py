import datetime
import json


class FileIsNotCorrectError(Exception):
    def __init__(self, *arg):
        pass


#Возвращает кортеж из первого числа текущего месяца и текущую дату
def request_time():
    date_now = datetime.datetime.now().date()  #Получаем текущую дату в формате 2022-07-01
    month_now = date_now.strftime("%m")  #Получаем номер текущего месяца в фомате - 07
    year_now = str(date_now.year)  #Получаем номер текущего года в формате - 2022
    the_beginning_of_the_month = year_now + '-' + month_now + '-01'  #Получаем дату начала текущего месяца в формате 2022-07-01
    return the_beginning_of_the_month, str(date_now)


class Configuration:
    def __init__(self):
        default_configuration = {'url_server_jira': 'http://192.168.100.230:8080/', 'login': '', 'password': '',
                                 'launch_mode': 'noprint', 'date_start': '', 'date_end': '', 'timeout_hide': 10000,
                                 'point_size': 11, 'bold': False}
        try:
            with open('config.json', 'r', encoding='utf-8') as f_conf:
                self.configuration = json.load(f_conf)
                print('Считан файл конфигурации ' + f_conf.name)
            if self.configuration.keys() != default_configuration.keys():
                raise FileIsNotCorrectError('Содержимое файла ' + f_conf.name + ' не корректно')
        except (FileNotFoundError, FileIsNotCorrectError) as log:
            print(log)
            self.configuration = default_configuration
            print('Создана новая конфигурация!', self.configuration)
            self.save_configuration()

    def get_configuration(self):
        return self.configuration

    def get_url_server_jira(self):
        return self.configuration['url_server_jira']

    def get_login(self):
        return self.configuration['login']

    def get_password(self):
        return self.configuration['password']

    def get_timeout_hide(self):
        return self.configuration['timeout_hide']

    def get_point_size(self):
        return self.configuration['point_size']

    def get_bold(self):
        return self.configuration['bold']

    def get_launch_mode(self):
        return self.configuration['launch_mode']

    def get_configuration_tuple(self):
        return tuple(self.configuration.values())

    def get_date(self):
        return self.configuration['date_start'], self.configuration['date_end']

    def set_url_server_jira(self, url_server_jira):
        self.configuration['url_server_jira'] = url_server_jira
        self.save_configuration()

    def set_login(self, login):
        self.configuration['login'] = login
        self.save_configuration()

    def set_password(self, password):
        self.configuration['password'] = password
        self.save_configuration()

    def set_launch_mode(self, launch_mode):
        self.configuration['launch_mode'] = launch_mode
        self.save_configuration()

    def set_url_login_password(self, url_server_jira, login, password):
        self.configuration['url_server_jira'] = url_server_jira
        self.configuration['login'] = login
        self.configuration['password'] = password
        self.save_configuration()

    def save_configuration(self):
        try:
            with open('config.json', 'w', encoding='utf-8') as f_conf:
                json.dump(self.configuration, f_conf, indent=4, ensure_ascii=False)
                print('Конфигурация успешно сохранена')
            return True
        except FileNotFoundError:
            print('Ошибка открытия файла ' + f_conf.name + 'для записи')
            return False

