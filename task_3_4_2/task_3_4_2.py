import math
from concurrent import futures
from statistics import mean
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Environment, FileSystemLoader
import pdfkit

dataframe_published_at = pd.read_csv("csv_3_3_1.csv")


def begin_processes(args):
    name_of_vacancy = args[0]
    year = args[1]
    pr_dataframe = pd.read_csv(f'created_csv_by_year\\chunk_{year}.csv')
    pr_dataframe["salary"] = pr_dataframe.apply(
        lambda row: process_salaries(row["salary_from"], row["salary_to"], row["salary_currency"],
                                     row["published_at"][:7].split("-")), axis=1)
    pr_dataframe_vacancies = pr_dataframe[pr_dataframe["name"].str.contains(name_of_vacancy)]
    salary_by_year = {year: []}
    vacancy_by_year = {year: 0}
    inp_vacancy_salary = {year: []}
    inp_vacancy_count = {year: 0}
    salary_by_year[year] = int(pr_dataframe['salary'].mean())
    vacancy_by_year[year] = len(pr_dataframe)
    inp_vacancy_salary[year] = int(pr_dataframe_vacancies['salary'].mean())
    inp_vacancy_count[year] = len(pr_dataframe_vacancies)
    return [salary_by_year, vacancy_by_year, inp_vacancy_salary, inp_vacancy_count]


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


if __name__ == "__main__":
    class CreateCSV:
        def __init__(self, name_file):
            self.dataframe = pd.read_csv(name_file)
            self.dataframe["years"] = self.dataframe["published_at"].apply(lambda date: int(date[:4]))
            self.all_years = list(self.dataframe["years"].unique())
            for year in self.all_years:
                data = self.dataframe[self.dataframe["years"] == year]
                data.iloc[:, :6].to_csv(f"created_csv_by_year\\chunk_{year}.csv", index=False)


    class InputConnect:
        def __init__(self):
            self.name_file = input("Введите название файла: ")
            self.name_vacancy = input("Введите название профессии: ")


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
        def __init__(self, vac_name, dicts_by_year):
            self.generate_image(vac_name, dicts_by_year)
            self.generate_pdf(vac_name, dicts_by_year)

        @staticmethod
        def generate_image(vac_name, dicts_by_year):
            x_nums = np.arange(len(dicts_by_year[0].keys()))
            width = 0.4
            x_first_list = x_nums - width / 2
            x_second_list = x_nums + width / 2
            figure = plt.figure()
            ax = figure.add_subplot(221)
            ax.set_title("Уровень зарплат по годам")
            ax.bar(x_first_list, dicts_by_year[0].values(), width, label="средняя з/п")
            ax.bar(x_second_list, dicts_by_year[1].values(), width, label=f"з/п {vac_name.lower()}")
            ax.set_xticks(x_nums, dicts_by_year[0].keys(), rotation="vertical")
            ax.tick_params(axis="both", labelsize=8)
            ax.legend(fontsize=8)
            ax.grid(True, axis="y")
            ax = figure.add_subplot(222)
            ax.set_title("Количество вакансий по годам")
            ax.bar(x_first_list, dicts_by_year[2].values(), width, label="Количество вакансий")
            ax.bar(x_second_list, dicts_by_year[3].values(), width, label=f"Количество вакансий \n{vac_name.lower()}")
            ax.set_xticks(x_nums, dicts_by_year[2].keys(), rotation="vertical")
            ax.tick_params(axis="both", labelsize=8)
            ax.legend(fontsize=8)
            ax.grid(True, axis="y")
            plt.tight_layout()
            plt.savefig("graph.png")

        @staticmethod
        def generate_pdf(vac_name, dicts_by_year):
            environment = Environment(loader=FileSystemLoader('..'))
            temp = environment.get_template("pdf_template.html")
            pdf_temp = temp.render(
                {'name': vac_name, 'by_year': dicts_by_year})
            all_options = {'enable-local-file-access': None}
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
            pdfkit.from_string(pdf_temp, 'report_3_4_2.pdf', configuration=config, options=all_options)


    input_connect = InputConnect()
    file = input_connect.name_file
    vacancy = input_connect.name_vacancy
    make_csv = CreateCSV(file)
    dataframe = make_csv.dataframe
    years = make_csv.all_years
    dataframe["salary"] = dataframe.apply(
        lambda row: process_salaries(row["salary_from"], row["salary_to"], row["salary_currency"],
                                     row["published_at"][:7].split("-")), axis=1)
    salaries_by_year = {}
    vacancies_by_year = {}
    inp_vacancy_salary = {}
    inp_vacancy_count = {}
    executor = futures.ProcessPoolExecutor()
    processes = []
    for year in years:
        arguments = (vacancy, year)
        returned_list = executor.submit(begin_processes, arguments).result()
        salaries_by_year.update(returned_list[0])
        vacancies_by_year.update(returned_list[1])
        inp_vacancy_salary.update(returned_list[2])
        inp_vacancy_count.update(returned_list[3])
    print("Динамика уровня зарплат по годам:", sort_dictionary(salaries_by_year))
    print("Динамика количества вакансий по годам:", sort_dictionary(vacancies_by_year))
    print("Динамика уровня зарплат по годам для выбранной профессии:", sort_dictionary(inp_vacancy_salary))
    print("Динамика количества вакансий по годам для выбранной профессии:", sort_dictionary(inp_vacancy_count))
    dicts_list_by_year = [sort_dictionary(salaries_by_year), sort_dictionary(inp_vacancy_salary),
                          sort_dictionary(vacancies_by_year), sort_dictionary(inp_vacancy_count)]
    report = Report(input_connect.name_vacancy, dicts_list_by_year)
