import math
import os
import pandas as pd
from multiprocessing import Process, Queue

pd.options.mode.chained_assignment = None


class InputConnect:
    def __init__(self):
        self.file_name = input('Введите название файла: ')
        self.profession_name = input('Введите название профессии: ')


def make_salary(x, currencies):
    salary_to = x.loc['salary_to']
    published_at = x.loc['published_at']
    salary_currency = x.loc['salary_currency']
    salary_from = x.loc['salary_from']
    date_published = published_at[:7]
    if math.isnan(salary_to) or math.isnan(salary_from):
        salary = salary_to if math.isnan(salary_from) else salary_from
    else:
        salary = math.floor((salary_from + salary_to) / 2)
    if salary_currency != 'RUR':
        return math.floor(salary * currencies.loc[currencies['date'] == date_published][salary_currency].values[0])
    return salary


def fill_dataframe(dataframe, currencies):
    working_currencies = list(currencies.loc[:, ~currencies.columns.isin(['date', 'Unnamed: 0'])].columns.values) + [
        'RUR']
    dataframe = dataframe[dataframe['salary_currency'].isin(working_currencies)]
    dataframe['salary'] = dataframe.apply(lambda x: make_salary(x, currencies), axis=1)
    dataframe.drop(columns=['salary_from', 'salary_to', 'salary_currency'], inplace=True)
    dataframe = dataframe.reindex(columns=['name', 'salary', 'area_name', 'published_at'], copy=True)
    return dataframe


def make_year_statistic(name_file, profession_name, queue, currencies):
    dataframe = pd.read_csv(name_file)
    dataframe = fill_dataframe(dataframe, currencies)
    data_profession = dataframe[dataframe['name'].str.contains(profession_name, case=False)]
    queue.put([int(dataframe['published_at'].values[0][:4]), dataframe.shape[0], math.floor(dataframe['salary'].mean()),
               data_profession.shape[0], math.floor(data_profession['salary'].mean()), dataframe])


def make_area_statistics():
    global vacancy_num_by_area, salary_by_area
    dataframe = pd.concat(dataframe_res, ignore_index=True)
    all_vac_num = dataframe.shape[0]
    vac_percent = int(all_vac_num * 0.01)

    data = dataframe.groupby('area_name')['name'] \
        .count() \
        .apply(lambda x: round(x / all_vac_num, 4)) \
        .sort_values(ascending=False) \
        .head(10) \
        .to_dict()
    vacancy_num_by_area = data

    area_vac_num = dataframe.groupby('area_name')['name'] \
        .count() \
        .loc[lambda x: x > vac_percent] \
        .to_dict()

    data = dataframe.loc[dataframe['area_name'].isin(area_vac_num.keys())] \
        .groupby('area_name')['salary'] \
        .mean() \
        .apply(lambda x: math.floor(x)) \
        .sort_values(ascending=False) \
        .head(10) \
        .to_dict()
    salary_by_area = data


def make_year_statistics():
    global vacancy_num_by_year, salary_by_year, vacancy_num_profession_by_year, salary_profession_by_year, dataframe_res
    queue = Queue()
    process = []
    currencies = pd.read_csv('csv_files/currencies.csv')
    for name_file in os.listdir(user_input.file_name):
        p = Process(target=make_year_statistic,
                    args=(user_input.file_name + '/' + name_file, user_input.profession_name, queue, currencies.copy()))
        process.append(p)
        p.start()
    for p in process:
        p.join(1)
        data = queue.get()
        vacancy_num_by_year[data[0]] = data[1]
        salary_by_year[data[0]] = data[2]
        vacancy_num_profession_by_year[data[0]] = data[3]
        salary_profession_by_year[data[0]] = data[4]
        dataframe_res.append(data[5])
    vacancy_num_by_year = dict(sorted(vacancy_num_by_year.items(), key=lambda i: i[0]))
    salary_by_year = dict(sorted(salary_by_year.items(), key=lambda i: i[0]))
    vacancy_num_profession_by_year = dict(sorted(vacancy_num_profession_by_year.items(), key=lambda i: i[0]))
    salary_profession_by_year = dict(sorted(salary_profession_by_year.items(), key=lambda i: i[0]))


def print_statistics():
    print(f'Динамика уровня зарплат по годам: {salary_by_year}')
    print(f'Динамика количества вакансий по годам: {vacancy_num_by_year}')
    print(f'Динамика уровня зарплат по годам для выбранной профессии: {salary_profession_by_year}')
    print(f'Динамика количества вакансий по годам для выбранной профессии: {vacancy_num_profession_by_year}')
    print(f'Уровень зарплат по городам (в порядке убывания): {salary_by_area}')
    print(f'Доля вакансий по городам (в порядке убывания): {vacancy_num_by_area}')


if __name__ == '__main__':
    vacancy_num_by_year = {}
    salary_by_year = {}
    vacancy_num_profession_by_year = {}
    salary_profession_by_year = {}
    vacancy_num_by_area = {}
    salary_by_area = {}
    dataframe_res = []
    user_input = InputConnect()
    make_year_statistics()
    make_area_statistics()
    print_statistics()
