import math
import pandas as pd
import sqlite3

currencies = {"BYR": 1, "EUR": 2, "KZT": 3, "UAH": 4, "USD": 5}
dataframe = pd.read_csv("../csv_files/vacancies_dif_currencies.csv")
connection = sqlite3.connect("task_3_5.sqlite")
first_cursor = connection.cursor()
dataframe["published_at"] = dataframe["published_at"].apply(lambda date: date[:7])


def process_salaries(row):
    value_of_currency = 0
    salary_currency = row.loc['salary_currency']
    published_at = row.loc['published_at']
    salary_from = row.loc['salary_from']
    salary_to = row.loc['salary_to']
    if salary_currency == 'RUR':
        value_of_currency = 1
    elif salary_currency in ['BYN', 'BYR', 'EUR', 'KZT', 'UAH', 'USD']:
        salary_currency.replace('BYN', 'BYR')
        value_of_currency = \
            first_cursor.execute("SELECT * FROM currencies WHERE date == :published_at",
                                 {"published_at": published_at}).fetchone()[
                currencies[salary_currency]]

    if math.isnan(salary_to) or math.isnan(salary_from):
        res_salary = salary_to if math.isnan(salary_from) else salary_from
    else:
        res_salary = math.floor((salary_from + salary_to) / 2)
    if not (math.isnan(res_salary)):
        return math.floor(res_salary * value_of_currency)
    return res_salary


dataframe['salary'] = dataframe.apply(lambda x: process_salaries(x), axis=1)
dataframe.drop(columns=['salary_from', 'salary_to', 'salary_currency'], inplace=True)
connect = sqlite3.connect("vacancies_dif_currencies.sqlite")
cursor = connection.cursor()
dataframe.to_sql(name="vacancies_dif_currencies", con=connect, if_exists='replace', index=False)
connect.commit()
