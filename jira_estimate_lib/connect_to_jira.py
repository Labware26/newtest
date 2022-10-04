from re import search
from jira import JIRA


class ConnectionToJIRA:
    """Ждет в себя 3 параметра: адрес сервера JIRA, логин и пароль"""
    def __init__(self, url_server_jira: str, login_user: str, password_user: str):
        self.connection_status = 1
        try:
            jira_options = {'server': url_server_jira}
            self.jira = JIRA(options=jira_options, basic_auth=(login_user, password_user), max_retries=0)
            print('Успешное подключение к серверу!')
        except Exception as jira_error_log:
            jira_error_log = str(jira_error_log)
            if search(r'Unauthorized', jira_error_log) is not None:
                self.connection_status = 2
                print('Ошибка авторизации!!')
                print(url_server_jira, login_user, password_user)
            elif search(r'Max retries exceeded with', jira_error_log) is not None:
                self.connection_status = 3
                print('Ошибка подключения')
            print(jira_error_log)

    def getConnection(self) -> JIRA:
        """Получаем экземпляр подключения к JIRA"""
        return self.jira

    def connectionStatus(self) -> int:
        """Позволяет получить статус подключения к JIRA(1-Подключено, 2-Ошибка авторизации, 3-Ошибка подключения)"""
        return self.connection_status
