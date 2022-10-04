from re import search
import datetime
from github.jira_estimate_lib.cases import Cases


class FromJiraResult(Cases):
    def __init__(self, connect_to_jira, config):
        super().__init__()
        self.config = config
        self.from_jira_result = dict()
        self.jira = connect_to_jira.getConnection()
        self.issue_error = 'Проблемы с оценкой!:\n'
        self.cases_error = 'Кейсы без оценки:\n'
        with open('person_list.ini', 'r', encoding='utf-8') as f_n:
            file_person_list = f_n.read().split()
        self.request_date = config.get_date()
        if config.get_date()[0] == '' or config.get_date()[1] == '':
            self.request_date = self.__request_time()  #Получаем даты текущего месяца для выгрузки
        for name in file_person_list:
            jql_executor = 'cf[10110] >= "' + self.request_date[0] + ' 06:00" AND cf[10110] <= "' + self.request_date[1] + ' 22:00" AND assignee in (' + name + ')'
            jql_tester = '"Дата проверки" >= "' + self.request_date[0] + ' 06:00" AND "Дата проверки" <= "' + self.request_date[1] + ' 22:00" AND "Испытатель/тестировщик" in (' + name + ')'
            issues_list_executor = self.__get_issue_list(self.jira, jql_executor)
            issues_list_tester = self.__get_issue_list(self.jira, jql_tester)
            self.from_jira_result.update(self.__from_jira_rezult(self.jira, issues_list_executor, issues_list_tester))
            if config.get_launch_mode() != 'print':
                break

    @staticmethod
    def __get_issue_list(jira, jql):
        start = 0
        leng = 50
        issues_list = None
        while True:
            if issues_list == None:
                issues_list = jira.search_issues(jql, start, leng)  #2 параметр говорит место старта, 3 сколько задач вычитать
            else:
                issues_list.extend(jira.search_issues(jql, start, leng))
            start += 50
            if start > issues_list.total:
                break
        return issues_list

    def __from_jira_rezult(self, jira, issues_list_executor, issues_list_tester):
        if issues_list_executor is not None:
            for i in issues_list_executor:
                issue = jira.issue(i)
                if issue.fields.project.key == 'TS':
                    if issue.fields.assignee.name not in self.from_jira_result:
                        if issue.fields.customfield_10106 is not None:
                            self.from_jira_result[issue.fields.assignee.name] = {'name': self.short_name(issue.fields.assignee.displayName), 'issue': {str(issue): {'estimate': issue.fields.customfield_10106, 'dev_name': issue.fields.customfield_10108[0].fields.summary, 'date_close': search(r"\d{4}-\d{2}-\d{2}", issue.fields.resolutiondate).group()}}}
                        else:
                            self.from_jira_result[issue.fields.assignee.name] = {'name': self.short_name(issue.fields.assignee.displayName), 'issue': {str(issue): {'estimate': 0.0, 'dev_name': issue.fields.customfield_10108[0].fields.summary, 'date_close': search(r"\d{4}-\d{2}-\d{2}", issue.fields.resolutiondate).group()}}}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
                    else:
                        if issue.fields.customfield_10106 is not None:
                            self.from_jira_result[issue.fields.assignee.name]['issue'][str(issue)] = {'estimate': issue.fields.customfield_10106, 'dev_name': issue.fields.customfield_10108[0].fields.summary, 'date_close': search(r"\d{4}-\d{2}-\d{2}", issue.fields.resolutiondate).group()}
                        else:
                            self.from_jira_result[issue.fields.assignee.name]['issue'][str(issue)] = {'estimate': 0.0, 'dev_name': issue.fields.customfield_10108[0].fields.summary, 'date_close': search(r"\d{4}-\d{2}-\d{2}", issue.fields.resolutiondate).group()}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
                else:
                    if issue.fields.assignee.name not in self.from_jira_result:
                        if issue.fields.customfield_10106 is not None:
                            self.from_jira_result[issue.fields.assignee.name] = {'name': self.short_name(issue.fields.assignee.displayName), 'issue': {str(issue): {'estimate': issue.fields.customfield_10106, 'dev_name': issue.fields.project.key}}}
                        else:
                            self.from_jira_result[issue.fields.assignee.name] = {'name': self.short_name(issue.fields.assignee.displayName), 'issue': {str(issue): {'estimate': 0.0, 'dev_name': issue.fields.project.key}}}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
                    else:
                        if issue.fields.customfield_10106 is not None:
                            self.from_jira_result[issue.fields.assignee.name]['issue'][str(issue)] = {'estimate': issue.fields.customfield_10106, 'dev_name': issue.fields.project.key}
                        else:
                            self.from_jira_result[issue.fields.assignee.name]['issue'][str(issue)] = {'estimate': 0.0, 'dev_name': issue.fields.project.key}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
        if issues_list_tester is not None:
            for i in issues_list_tester:
                issue = jira.issue(i)
                if issue.fields.customfield_10408.name not in self.from_jira_result:
                    try:
                        if issue.fields.customfield_10412 is not None:
                            self.from_jira_result[issue.fields.customfield_10408.name] = {'name': self.short_name(issue.fields.customfield_10408.displayName), 'issue': {str(issue): {'estimate': issue.fields.customfield_10412, 'dev_name': issue.fields.project.key}}}
                        else:
                            self.from_jira_result[issue.fields.customfield_10408.name] = {'name': self.short_name(issue.fields.customfield_10408.displayName), 'issue': {str(issue): {'estimate': 0.0, 'dev_name': issue.fields.project.key}}}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
                    except AttributeError:
                        self.from_jira_result[issue.fields.customfield_10408.name] = {'name': self.short_name(issue.fields.customfield_10408.displayName), 'issue': {str(issue): {'estimate': 0.0, 'dev_name': issue.fields.project.key}}}
                        self.issue_error += str(issue) + ' - поля с оценкой не существует\n'
                else:
                    try:
                        if issue.fields.customfield_10412 is not None:
                            self.from_jira_result[issue.fields.customfield_10408.name]['issue'][str(issue)] = {'estimate': issue.fields.customfield_10412, 'dev_name': issue.fields.project.key}
                        else:
                            self.from_jira_result[issue.fields.customfield_10408.name]['issue'][str(issue)] = {'estimate': 0.0, 'dev_name': issue.fields.project.key}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
                    except AttributeError:
                        self.from_jira_result[issue.fields.customfield_10408.name]['issue'][str(issue)] = {'estimate': 0.0, 'dev_name': issue.fields.project.key}
                        self.issue_error += str(issue) + ' - поля с оценкой не существует\n'
        return self.from_jira_result

    # производит выборку по пройденным кейсам и пакует в словарь
    #{'Бурцев Вячеслав': {'name': 'Бурцев Вячеслав', 'issue': {'TSZ-1051': {'estimate': 2.0, 'dev_name': 'TSZ'}, 'TSZ-1049': {'estimate': 0.5, 'dev_name': 'TSZ'}}}
    def get_from_cases_rezult(self) -> dict:
        cases_dict = self.completed_cases(self.request_date)  # Получаем выборку по пройденным тест-кейсам
        print('Получаем информацию по кейсам из базы')
        from_cases_rezult = dict()
        if cases_dict != {}:
            for key_name in cases_dict.keys():
                for tsz in cases_dict[key_name]:
                    issue = self.jira.issue(tsz)
                    if key_name not in from_cases_rezult:
                        if issue.fields.customfield_10106 != None:
                            from_cases_rezult[key_name] = {'name': key_name, 'issue': {tsz: {'estimate': issue.fields.customfield_10106, 'dev_name': issue.fields.project.key}}}
                        else:
                            from_cases_rezult[key_name] = {'name': key_name, 'issue': {tsz: {'estimate': 0.0, 'dev_name': issue.fields.project.key}}}
                            self.cases_error += tsz + ' - задача не оценена\n'
                    else:
                        if issue.fields.customfield_10106 != None:
                            from_cases_rezult[key_name]['issue'][tsz] = {'estimate': issue.fields.customfield_10106, 'dev_name': issue.fields.project.key}
                        else:
                            from_cases_rezult[key_name]['issue'][tsz] = {'estimate': 0.0, 'dev_name': issue.fields.project.key}
                            self.cases_error += tsz + ' - задача не оценена\n'
        print(from_cases_rezult)
        print(self.cases_error)
        return from_cases_rezult

    def get_from_jira_result(self):
        return self.from_jira_result

    def get_issue_error(self):
        return self.issue_error

    def get_cases_error(self):
        return self.cases_error

    def get_request_time(self):
        return self.request_date

    # Считаем оценки всех задач по сотрудникам и пакуем в словарь
    # {'Имя1': оценка. 'Имя1': оценка}
    def get_all_estimate(self):
        person_dict = dict()
        if self.from_jira_result != {}:
            for person in self.from_jira_result.keys():
                estimate_result = 0.0
                for issue in self.from_jira_result[person]['issue']:
                    estimate_result = round(estimate_result + self.from_jira_result[person]['issue'][issue]['estimate'], 1)
                person_dict[self.from_jira_result[person]['name']] = estimate_result
        else:
            person_dict['Закрытых задач нет'] = 0.0
        return person_dict

    # Считаем оценки всех кейсов по сотрудникам и пакуем в словарь
    # {'Имя1': оценка. 'Имя1': оценка}
    def get_cases_estimate(self, from_cases_rezult):
        cases_estimation_dict = dict()
        if from_cases_rezult != {}:
            for name in from_cases_rezult.keys():
                estimate_result = 0.0
                for tsz in from_cases_rezult[name]['issue']:
                    estimate_result = round(estimate_result + from_cases_rezult[name]['issue'][tsz]['estimate'], 1)
                cases_estimation_dict[from_cases_rezult[name]['name']] = estimate_result
        else:
            cases_estimation_dict['Пройденных кейсов нет'] = 0.0
        # Выводим результат в консоль
        for name_key in cases_estimation_dict:
            print(name_key, cases_estimation_dict[name_key])
        return cases_estimation_dict

    # Суммирует оценки сотрудников по проектам.
    # {'Фамилия Имя': {'название проекта1': оценка, 'название проекта1': оценка}
    def get_estimate_to_project(self) -> dict:
        estimate_to_project = dict()
        for person in self.from_jira_result.keys():
            name_project_set = set()
            # Делаем множество из имен проектов сотрудника
            for issue in self.from_jira_result[person]['issue']:
                name_project_set.add(self.from_jira_result[person]['issue'][issue]['dev_name'])
            dev = dict()
            # Создаем словать из проектов и каждому присваиваем оценку 0
            for ittr in name_project_set:
                dev[ittr] = 0.0
            # Суммируем оценки по проектно
            for issue_num in self.from_jira_result[person]['issue']:
                dev[self.from_jira_result[person]['issue'][issue_num]['dev_name']] = round(dev[self.from_jira_result[person]['issue'][issue_num]['dev_name']] + self.from_jira_result[person]['issue'][issue_num]['estimate'], 1)
            estimate_to_project[self.from_jira_result[person]['name']] = dev
        return estimate_to_project  # {'Фамилия Имя': {'название проекта1': оценка, 'название проекта1': оценка}

    @staticmethod
    def short_name(name: str) -> str:
        short_name = search(r'^\S+\s\S+', name).group()
        return short_name

    # Получаем даты для выборки за текущий месяц
    @staticmethod
    def __request_time():
        date_now = datetime.datetime.now().date()  # Получаем текущую дату в формате 2022-07-01
        month_now = date_now.strftime("%m")  # Получаем номер текущего месяца в фомате - 07
        year_now = str(date_now.year)  # Получаем номер текущего года в формате - 2022
        the_beginning_of_the_month = year_now + '-' + month_now + '-01'  # Получаем дату начала текущего месяца в формате 2022-07-01
        return the_beginning_of_the_month, str(date_now)
