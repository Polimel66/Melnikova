import csv
import re
from prettytable import PrettyTable, ALL
from datetime import datetime


class InputConect:
    """Отвечает за обработку параметров вводимых пользователем: фильтры, сортировка, диапазон вывода, требуемые столбцы,
     а также за печать таблицы на экран.

     Attributes:
         file_name (str): Имя файла
         filtering_parameter (str): Параметр фильтрации
         sorting_parameter (str): Параметр сортировки
         is_reverse_sort_order (bool): булевая переменная определяющая порядок сортировки (обратный или нет)
         output_range (list): диапазон вывода
         required_columns (list): требуемые столбцы
    """

    def __init__(self):
        """Инициализирует объект InputConect

        Args:
            file_name (str): Имя файла
            filtering_parameter (str): Параметр фильтрации
            sorting_parameter (str): Параметр сортировки
            is_reverse_sort_order (bool): булевая переменная определяющая порядок сортировки (обратный или нет)
            required_columns (list): требуемые столбцы
        """
        self.file_name, self.filtering_parameter, self.sorting_parameter, self.is_reverse_sort_order, self.output_range, self.required_columns = InputConect.entering_requests()

    @staticmethod
    def sort_experience(vacancy):
        """Отвечает за сортировку по параметру Опыт работы. Это метод будет использован как аргумент для Sort.

        Args:
            vacancy (Vacancy): Объект класса Vacancy, содержащий информацию о вакансии

        Returns:
            int: возвращает цифру равную максимальному числу лет, которое нужно отработать
        """
        experience = vacancy.experience_id
        if experience == 'noExperience':
            return 0
        elif experience == 'between1And3':
            return 3
        elif experience == 'between3And6':
            return 6
        return 7

    @staticmethod
    def entering_requests():
        """Отвечает за ввод запросов пользователя

        Returns:
            tuple: коллекция, содержащая параметры введенные пользователем (имя файла, параметр сортировки,
             параметр фильтрации, порядок сортировки, диапазон вывода и требуемые столбцы)
        """
        print('Введите название файла:', end=' ')
        name_file = input()
        print('Введите параметр фильтрации:', end=' ')
        filtering_parameter = input()
        print('Введите параметр сортировки:', end=' ')
        sorting_parameter = input()
        print('Обратный порядок сортировки (Да / Нет):', end=' ')
        is_reverse = input()
        print('Введите диапазон вывода:', end=' ')
        serial_numbers_vacancies = input().split()
        print('Введите требуемые столбцы:', end=' ')
        column_headers_str = input()
        if is_reverse == 'Да':
            is_reverse = True
        elif is_reverse == '' or is_reverse == 'Нет':
            is_reverse = False
        else:
            print('Порядок сортировки задан некорректно')
            exit()

        if column_headers_str != "":
            column_headers = column_headers_str.split(', ')
        else:
            column_headers = []
        all_parameters = ['Навыки', 'Оклад', 'Дата публикации вакансии', 'Опыт работы',
                          'Премиум-вакансия', 'Идентификатор валюты оклада', 'Описание',
                          'Название', 'Название региона', 'Компания']
        if sorting_parameter != '' and sorting_parameter not in all_parameters:
            print('Параметр сортировки некорректен')
            exit()
        if ': ' not in filtering_parameter and '' != filtering_parameter:
            print('Формат ввода некорректен')
            exit()
        elif filtering_parameter.split(': ')[0] not in all_parameters \
                and '' != filtering_parameter:
            print('Параметр поиска некорректен')
            exit()
        return name_file, filtering_parameter, sorting_parameter, is_reverse, serial_numbers_vacancies, column_headers

    @staticmethod
    def print_table(vacancies, output_range, required_columns):
        """Отвечает за формирование и печать таблицы

        Args:
            vacancies (list): Список словарей, содержащих информацию о вакансиях (столбец - значение)
            output_range (list): Диапазон вывода таблицы
            required_columns (list): Требуемые для вывода столбцы

        Никаких значений не возвращает, но печатает таблицу в консоль
        """
        table = PrettyTable(hrules=ALL, align='l')
        flag = True
        counter = 0
        for vacancy in vacancies:
            if flag:
                table.field_names = vacancy.keys()
                table.max_width = 20
                flag = False
            table.add_row(InputConect.trim_line(vacancy).values())
            counter += 1
        if counter == 0:
            print('Ничего не найдено')
            exit()
        range_length = len(output_range)
        start = 0
        end = counter
        if range_length == 1:
            start = int(output_range[0]) - 1
        elif range_length == 2:
            start = int(output_range[0]) - 1
            end = int(output_range[1]) - 1
        table.add_autoindex('№')
        if len(required_columns) != 0:
            required_columns.insert(0, "№")
            table = table.get_string(start=start, end=end, fields=required_columns)
        else:
            table = table.get_string(start=start, end=end)
        print(table)

    @staticmethod
    def trim_line(vacancy):
        """Обрезает информацию, которая длиннее 100 символов

        Args:
            vacancy (dict): словарь содержащий информацию о вакансии

        Returns:
            dict: словарь с информацией обрезанной до 100 символов
        """
        resultVacancy = {}
        for key, val in vacancy.items():
            if len(str(val)) > 100:
                val = val[:100] + '...'
            resultVacancy[key] = val
        return resultVacancy

    def data_processing(self, vacancies):
        """Обрабатывает данные (вызывает методы сортировки, фильтрации и форматирования)

        Args:
            vacancies (list): список объектов Vacancy, содержащих информацию о вакансиях
        """
        dic_sorting = {'Навыки': lambda vacancy: len(vacancy.key_skills.split('\n')),
                       'Оклад': lambda vacancy: (float(vacancy.salary.salary_from) * currency_to_rub[
                           vacancy.salary.salary_currency] + float(
                           vacancy.salary.salary_to) * currency_to_rub[vacancy.salary.salary_currency]) / 2,
                       'Дата публикации вакансии': lambda vacancy: vacancy.published_at,
                       'Опыт работы': self.sort_experience,
                       'Премиум-вакансия': lambda vacancy: vacancy.premium,
                       'Описание': lambda vacancy: vacancy.description,
                       'Название': lambda vacancy: vacancy.name,
                       'Название региона': lambda vacancy: vacancy.area_name,
                       'Компания': lambda vacancy: vacancy.employer_name}
        filter_dictionary = {'Навыки': self.check_occurrence_skills,
                             'Оклад': lambda sample, vacancy: int(vacancy.salary.salary_from) <= int(sample) <= int(
                                 vacancy.salary.salary_to),
                             'Дата публикации вакансии': lambda sample, vacancy: sample == datetime.strptime(
                                 vacancy.published_at, '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y'),
                             'Опыт работы': lambda sample, vacancy: sample == vacancy.experience_id,
                             'Премиум-вакансия': lambda sample, vacancy: sample == vacancy.premium,
                             'Идентификатор валюты оклада': lambda sample,
                                                                   vacancy: sample == vacancy.salary.salary_currency,
                             'Описание': lambda sample, vacancy: sample == vacancy.description,
                             'Название': lambda sample, vacancy: sample == vacancy.name,
                             'Название региона': lambda sample, vacancy: sample == vacancy.area_name,
                             'Компания': lambda sample, vacancy: sample == vacancy.employer_name}
        dic_functions = {'Дата публикации вакансии_value': lambda date:
        datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y'),
                         'True': lambda elem: dic_naming[elem], 'False': lambda elem: dic_naming[elem],
                         'noExperience': lambda elem: dic_naming[elem],
                         'between1And3': lambda elem: dic_naming[elem], 'between3And6': lambda elem: dic_naming[elem],
                         'moreThan6': lambda elem: dic_naming[elem],
                         'Salary_Value': self.salary_formation}
        dic_naming = {'name': 'Название', 'description': 'Описание', 'key_skills': 'Навыки',
                      'experience_id': 'Опыт работы', 'premium': 'Премиум-вакансия', 'employer_name': 'Компания',
                      'area_name': 'Название региона', 'published_at': 'Дата публикации вакансии', 'True': 'Да',
                      'False': 'Нет',
                      'noExperience': 'Нет опыта', 'between1And3': 'От 1 года до 3 лет',
                      'between3And6': 'От 3 до 6 лет',
                      'moreThan6': 'Более 6 лет', 'Salary': 'Оклад'}
        rus_to_eng = {'Да': 'True',
                      'Нет': 'False',
                      'Нет опыта': 'noExperience', 'От 1 года до 3 лет': 'between1And3',
                      'От 3 до 6 лет': 'between3And6',
                      'Более 6 лет': 'moreThan6', 'Оклад': 'Salary',
                      'Манаты': 'AZN', 'Белорусские рубли': 'BYR', 'Евро': 'EUR',
                      'Грузинский лари': 'GEL', 'Киргизский сом': 'KGS', 'Тенге': 'KZT',
                      'Рубли': 'RUR', 'Гривны': 'UAH', 'Доллары': 'USD',
                      'Узбекский сум': 'UZS'
                      }
        if self.sorting_parameter != '':
            vacancies = InputConect.make_sort(vacancies, self.sorting_parameter, self.is_reverse_sort_order,
                                              dic_sorting)
        if self.filtering_parameter != '':
            vacancies = InputConect.make_filtering(vacancies, self.filtering_parameter, filter_dictionary, rus_to_eng)
        vacancies = InputConect.formatter(vacancies, dic_functions)
        InputConect.print_table(vacancies, self.output_range, self.required_columns)

    @staticmethod
    def formatter(vacancies, funcs):
        """Форматирует информацию (переводит на русский, вызывает методы форматирования даты и зарплаты)

        Args:
            vacancies (list): список объектов Vacancy, содержащих информацию о вакансиях
            funcs (dict): словарь функций, с помощью которого форматируется информация

        Returns:
            list: список словарей, содержащих отформатированную информацию о вакансиях
        """
        result = []
        for vacancy in vacancies:
            res = {'Название': vacancy.name,
                   'Описание': vacancy.description,
                   'Навыки': vacancy.key_skills,
                   'Опыт работы': vacancy.experience_id,
                   'Премиум-вакансия': vacancy.premium,
                   'Компания': vacancy.employer_name,
                   'Оклад': funcs['Salary_Value'](vacancy.salary),
                   'Название региона': vacancy.area_name,
                   'Дата публикации вакансии': vacancy.published_at}
            result_dic = {}
            for key, value in res.items():
                if key + '_value' in funcs.keys():
                    value = funcs[key + '_value'](value)
                elif value in funcs.keys():
                    value = funcs[value](value)
                result_dic[key] = value
            result.append(result_dic)
        return result

    @staticmethod
    def salary_formation(salary):
        """Форматирует зарплату, формирует строку для столбца Оклад

        Args:
            salary (Salary): Объект класса Salary, содержащий информацию о зарплате

        Returns:
            str: Сформированная строка оклада для таблицы
        """
        currency_dictionary = {'AZN': 'Манаты', 'BYR': 'Белорусские рубли', 'EUR': 'Евро',
                               'GEL': 'Грузинский лари', 'KGS': 'Киргизский сом', 'KZT': 'Тенге',
                               'RUR': 'Рубли', 'UAH': 'Гривны', 'USD': 'Доллары',
                               'UZS': 'Узбекский сум'}
        if salary.salary_gross == 'True':
            salary_gross = 'Без вычета налогов'
        else:
            salary_gross = 'С вычетом налогов'
        result = f'{format(int(salary.salary_from.split(".")[0]), ",").replace(",", " ")} - ' \
                 f'{format(int(salary.salary_to.split(".")[0]), ",").replace(",", " ")} ' \
                 f'({currency_dictionary[salary.salary_currency]}) ({salary_gross})'
        return result

    @staticmethod
    def check_occurrence_skills(sample: str, vacancy):
        """Метод для фильтрации по навыкам, проверяет вхождение всех навыков из параметра фильтрации
         в полный список навыков вакансии

        Args:
            sample (str): Навыки из параметра, которые должны входить в нужную нам вакансию
            vacancy (Vacancy): вакансия которая проверяется фильтром

        Returns:
            bool: True - вакансия подходит, False - вакансия не прошла фильтр
        """
        if ', ' in sample:
            sampleList = sample.split(', ')
        else:
            sampleList = [sample]
        comparedList = vacancy.key_skills.split('\n')
        for skill in sampleList:
            if skill not in comparedList:
                return False
        return True

    @staticmethod
    def make_filtering(vacancies: list, parameter, filter_dictionary, rus_to_eng):
        """Отвечает за осуществление фильтрации

        Args:
            vacancies (list): Список объектов Vacancy, содержащих информацию о вакансиях
            parameter (list): Список содержащий параметр фильтрации
            filter_dictionary (dict): Словарь функций для фильтрации по каждому из столбцов
            rus_to_eng (dict): Словарь перевода информации на русский язык

        Returns:
            list: Отфильтрованный список вакансий (объектов класса Vacancy)
        """
        res_vacancies = []
        parameter = parameter.split(': ')
        for vacancy in vacancies:
            if parameter[1] in rus_to_eng.keys():
                sample = rus_to_eng[parameter[1]]
            else:
                sample = parameter[1]

            if not (filter_dictionary[parameter[0]](sample, vacancy)):
                continue
            res_vacancies.append(vacancy)
        return res_vacancies

    @staticmethod
    def make_sort(vacancies: list, parameter, is_reverse, dic_sorting):
        """Сортирует вакансии

        Args:
            vacancies (list): Список объектов Vacancy, содержащих информацию о вакансиях
            parameter (str): Параметр сортировки
            is_reverse (bool): Порядок сортировки
            dic_sorting (dict): Словарь функций для сортировки

        Returns:
            list: Отсортированные список вакансий (объектов класса Vacancy)
        """
        if parameter in dic_sorting.keys():
            vacancies.sort(key=dic_sorting[parameter], reverse=is_reverse)
        else:
            print('Параметр сортировки некорректен')
            exit()
        return vacancies


class Vacancy:
    """Класс для представления вакансии

    Attributes:
        name (str): Название вакансии
        description (str): Описание вакансии
        key_skills (str): Навыки
        experience_id (str): Опыт работы
        premium (str): Премиум-вакансия
        employer_name (str): Компания
        salary (Salary): объект класса Salary, содержащий в себе всю информацию о зарплате
        area_name (str): Название региона
        published_at (str): Дата и время публикации вакансии
    """

    def __init__(self, name, description, key_skills, experience_id, premium, employer_name, salary, area_name,
                 published_at):
        """Инициализирует объект Vacancy

        Args:
            name (str): Название вакансии
            description (str): Описание вакансии
            key_skills (str): Навыки
            experience_id (str): Опыт работы
            premium (str): Премиум-вакансия
            employer_name (str): Компания
            salary (Salary): объект класса Salary, содержащий в себе всю информацию о зарплате
            area_name (str): Название региона
            published_at (str): Дата и время публикации вакансии
        """
        self.name = name
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = premium
        self.employer_name = employer_name
        self.salary = salary
        self.area_name = area_name
        self.published_at = published_at


class Salary:
    """Класс для представления зарплаты

    Attributes:
        salary_from (str): Нижняя граница зарплаты
        salary_to (str): Верхняя граница зарплаты
        salary_gross (str): Оклад указан до вычета налогов
        salary_currency (str): Идентификатор валюты оклада
    """

    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        """Инициализирует объект Vacancy

        Args:
            salary_from (str): Нижняя граница зарплаты
            salary_to (str): Верхняя граница зарплаты
            salary_gross (str): Оклад указан до вычета налогов
            salary_currency (str): Идентификатор валюты оклада
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency


class DataSet:
    """Отвечает за чтение и подготовку данных из CSV-файла

    Attributes:
        file_name (str): Имя файла
        vacancies_objects (list): список объектов класса Vacancy, содержащих в себе информацию из файла после парсинга
    """

    def __init__(self, file_name):
        """Инициализирует объект DataSet, звпускает работу остальных методов для заполнения vacancies_objects

        Args:
            file_name (str): Имя файла
        """
        self.file_name = file_name
        self.vacancies_objects = DataSet.csv_filer(file_name)

    @staticmethod
    def csv_reader(name_file):
        """Отвечает за открывание и считывание csv файла

        Args:
            name_file (str): Имя файла

        Returns:
            tuple: Коллекция из двух элементов: первый - список заголовков, второй - список строк информации из файла
        """
        file = open(name_file, encoding='utf_8_sig')
        reader = csv.reader(file)
        data = []
        for i in reader:
            data.append(i)
        if len(data) == 0:
            print('Пустой файл')
            exit()
        elif len(data) == 1:
            print('Нет данных')
            exit()
        return data[0], data[1:]

    @staticmethod
    def csv_filer(name_file):
        """Отвечает за "чистку" считанной информации: убирает html теги, лишние пробелы.
        Формирует из полученной информации объекты класса Vacancy

        Args:
            name_file(str): Имя файла

        Returns:
            list: список объектов класса Vacancy, содержащих в себе информацию из файла после парсинга
        """
        headings, informations = DataSet.csv_reader(name_file)
        vacancies_objects = []
        for inf in informations:
            dic = {}
            if len(headings) == len(inf) and '' not in inf:
                for i in range(len(inf)):
                    if headings[i] != 'key_skills':
                        inf[i] = re.sub(r'<[^>]*>', '', inf[i], flags=re.S)
                        inf[i] = " ".join(inf[i].split())
                    dic[headings[i]] = inf[i]
                vacancies_objects.append(
                    Vacancy(dic['name'], dic['description'], dic['key_skills'], dic['experience_id'],
                            dic['premium'], dic['employer_name'],
                            Salary(dic['salary_from'], dic['salary_to'],
                                   dic['salary_gross'], dic['salary_currency']),
                            dic['area_name'], dic['published_at']))
        return vacancies_objects


def get_result():
    """Запускает программу
    """
    input_inf = InputConect()
    data_Set = DataSet(input_inf.file_name)
    input_inf.data_processing(data_Set.vacancies_objects)


# get_result()

currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}
