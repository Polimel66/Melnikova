import math
from statistics import mean
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Environment, FileSystemLoader
import pdfkit
from matplotlib import ticker


def process_salaries(salary_from, salary_to, salary_currency, published_at):
    published_at = published_at[1] + "/" + published_at[0]
    salary_currency_value = 0
    if salary_currency == "RUR":
        salary_currency_value = 1
    elif salary_currency != "RUR" and salary_currency in ["BYN", "BYR", "EUR",
                                                          "KZT", "UAH", "USD"]:
        salary_currency.replace("BYN", "BYR")
        dataframe_published_at_row = dataframe_published_at.loc[dataframe_published_at["date"] == published_at]
        salary_currency_value = dataframe_published_at_row[salary_currency].values[0]
    if math.isnan(salary_from) and not (math.isnan(salary_to)):
        return salary_to * salary_currency_value
    elif not (math.isnan(salary_from)) and math.isnan(salary_to):
        return salary_from * salary_currency_value
    elif not (math.isnan(salary_from)) and not (math.isnan(salary_to)):
        return mean([salary_from, salary_to]) * salary_currency_value


def sort_dictionary(dictionary):
    result_dict = {}
    sort_dict = sorted(dictionary)
    for key in sort_dict:
        result_dict[key] = dictionary[key]
    return result_dict


def sort_dictionary_area(dictionary):
    sorted_tuples = sorted(dictionary.items(), key=lambda elem: elem[1], reverse=True)[:10]
    sorted_dict = {k: v for k, v in sorted_tuples}
    return sorted_dict


class Report:
    def __init__(self, vac_name, region, dictionary_by_area, dictionary_by_year, other_vacancies):
        self.generate_image(vac_name, region, dictionary_by_area, dictionary_by_year, other_vacancies)
        self.generate_pdf(vac_name, region, dictionary_by_area, dictionary_by_year)

    @staticmethod
    def generate_image(vacancy_name, region, dictionary_by_area, dictionary_by_year, other_vacancies):
        all_cities = np.arange(len(dictionary_by_area[0].keys()))
        all_cities_names = {}
        for key, value in dictionary_by_area[0].items():
            if "-" in key or " " in key:
                key = key.replace("-", "-\n")
                key = key.replace(" ", "\n")
            all_cities_names[key] = value
        x_nums = np.arange(len(dictionary_by_year[0].keys()))
        width = 0.4
        x_first_list = x_nums
        figure = plt.figure()
        ax = figure.add_subplot(221)
        ax.set_title("Уровень зарплат по годам")
        ax.bar(x_first_list, dictionary_by_year[0].values(), width,
               label=f"з/п {vacancy_name.lower()} {region.lower()}")
        ax.set_xticks(x_nums, dictionary_by_year[0].keys(), rotation="vertical")
        ax.tick_params(axis="both", labelsize=8)
        ax.legend(fontsize=8)
        ax.grid(True, axis="y")
        ax = figure.add_subplot(222)
        ax.set_title("Количество вакансий по годам")
        ax.bar(x_first_list, dictionary_by_year[1].values(), width,
               label=f"Количество вакансий \n{vacancy_name.lower()} {region.lower()}")
        ax.set_xticks(x_nums, dictionary_by_year[1].keys(), rotation="vertical")
        ax.tick_params(axis="both", labelsize=8)
        ax.legend(fontsize=8)
        ax.grid(True, axis="y")
        ax = figure.add_subplot(223)
        ax.set_title("Уровень зарплат по городам")
        width = 0.8
        ax.barh(all_cities, dictionary_by_area[0].values(), width, align="center")
        ax.set_yticks(all_cities, labels=all_cities_names.keys(), horizontalalignment="right",
                      verticalalignment="center")
        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=6)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(100000))
        ax.invert_yaxis()
        ax.grid(True, axis="x")
        ax = figure.add_subplot(224)
        ax.set_title("Доля вакансий по городам")
        dictionary_by_area[1]["Другие"] = other_vacancies
        ax.pie(dictionary_by_area[1].values(), labels=dictionary_by_area[1].keys(), textprops={'size': 6},
               colors=["#ff8006", "#28a128", "#1978b5", "#0fbfd0", "#bdbe1c", "#808080", "#e478c3", "#8d554a",
                       "#9567be",
                       "#d72223", "#1978b5", "#ff8006"])
        ax.axis('equal')
        plt.tight_layout()
        plt.savefig("graph.png")

    @staticmethod
    def generate_pdf(vac_name, region, dictionary_by_area, dictionary_by_year):
        environment = Environment(loader=FileSystemLoader('..'))
        temp = environment.get_template("pdf_template.html")
        pdf_temp = temp.render(
            {'name': vac_name, 'reg': region, 'by_area': dictionary_by_area, 'by_year': dictionary_by_year,
             'keys_0_area': list(dictionary_by_area[0].keys()), 'values_0_area': list(dictionary_by_area[0].values()),
             'keys_1_area': list(dictionary_by_area[1].keys()), 'values_1_area': list(dictionary_by_area[1].values())})
        all_options = {'enable-local-file-access': None}
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_temp, 'report_3_4_3.pdf', configuration=config, options=all_options)


class InputConnect:
    def __init__(self):
        self.name_file = input("Введите название файла: ")
        self.name_vacancy = input("Введите название профессии: ")
        self.region = input("Введите название региона: ")


input_connect = InputConnect()
file_name = input_connect.name_file
vacancy = input_connect.name_vacancy
region = input_connect.region
dataframe = pd.read_csv(file_name)
dataframe["years"] = dataframe["published_at"].apply(lambda date: int(".".join(date[:4].split("-"))))
all_years = list(dataframe["years"].unique())
salaries_areas = {}
vacancies_areas = {}
inp_vacancy_salary = {}
inp_vacancy_count = {}
dataframe_published_at = pd.read_csv("csv_3_3_1.csv")
dataframe["salary"] = dataframe.apply(
    lambda row: process_salaries(row["salary_from"], row["salary_to"], row["salary_currency"],
                                 row["published_at"][:7].split("-")), axis=1)
count_vacancies = len(dataframe)
dataframe["count"] = dataframe.groupby("area_name")['area_name'].transform("count")
dataframe_normal = dataframe[dataframe['count'] >= 0.01 * count_vacancies]
cities = list(dataframe_normal["area_name"].unique())
other = len(dataframe[dataframe['count'] < 0.01 * count_vacancies]) / count_vacancies
for city in cities:
    dataframe_city = dataframe_normal[dataframe_normal['area_name'] == city]
    vacancies_areas[city] = round(len(dataframe_city) / len(dataframe), 4)
    salaries_areas[city] = int(dataframe_city['salary'].mean())
dataframe_vacancy = dataframe[dataframe["name"].str.contains(vacancy)]
for year in all_years:
    dataframe_vacancy_salary = dataframe_vacancy[
        (dataframe_vacancy['years'] == year) & (dataframe_vacancy['area_name'] == region)]
    if not dataframe_vacancy_salary.empty:
        inp_vacancy_salary[year] = int(dataframe_vacancy_salary['salary'].mean())
        inp_vacancy_count[year] = len(dataframe_vacancy_salary)
print("Уровень зарплат по городам (в порядке убывания):", sort_dictionary_area(salaries_areas))
print("Доля вакансий по городам (в порядке убывания):", sort_dictionary_area(vacancies_areas))
print("Динамика уровня зарплат по годам для выбранной профессии и региона:", sort_dictionary(inp_vacancy_salary))
print("Динамика количества вакансий по годам для выбранной профессии и региона:", sort_dictionary(inp_vacancy_count))
dictionaries_by_area = [sort_dictionary_area(salaries_areas), sort_dictionary_area(vacancies_areas)]
dictionaries_by_year = [sort_dictionary(inp_vacancy_salary), sort_dictionary(inp_vacancy_count)]
report = Report(vacancy, region, dictionaries_by_area, dictionaries_by_year, other)
