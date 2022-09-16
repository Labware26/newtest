from re import search
from typing import List


class Utils:
    @staticmethod
    def join_strings(str_list: List[str]) -> str:
        return ','.join(str_list)

    @staticmethod
    def short_name(name: str) -> str:
        short_name = search(r'^\S+\s\S+', name).group()
        return short_name

    @staticmethod
    def get_dict_by_list(list_rez: List[list]) -> dict:
        dict_rez = dict()
        for i in list_rez:
            if i[0] not in dict_rez:
                dict_rez[i[0]] = [i[1]]
            else:
                dict_rez[i[0]].append(i[1])
        # Преобразуем словарь, убрав из ключей отчество сотрудников
        dict_rez_short_name = {}
        for full_name in dict_rez.keys():
            dict_rez_short_name[Utils.short_name(full_name)] = dict_rez[full_name]

        return dict_rez_short_name


