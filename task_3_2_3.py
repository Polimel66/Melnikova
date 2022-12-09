import pandas as pd
from concurrent import futures

dictionaries = []


def begin_processes(args):
    name_of_vacancy = args[0]
    year = args[1]

    pr_dataframe = pd.read_csv(f'created_csv_by_year\\chunk_{year}.csv')
    pr_dataframe.loc[:, 'salary'] = pr_dataframe.loc[:, ['salary_from', 'salary_to']].mean(axis=1)
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


if __name__ == "__main__":

    class InputConnect:
        def __init__(self):
            self.name_file = input("Введите название файла: ")
            self.name_vacancy = input("Введите название профессии: ")


    class CreateCSV:
        def __init__(self, name_file):
            self.dataframe = pd.read_csv(name_file)
            self.dataframe["years"] = self.dataframe["published_at"].apply(lambda date: int(date[:4]))
            self.all_years = list(self.dataframe["years"].unique())
            for year in self.all_years:
                data = self.dataframe[self.dataframe["years"] == year]
                data.iloc[:, :6].to_csv(f"created_csv_by_year\\chunk_{year}.csv", index=False)


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


    input = InputConnect()
    file_name, vacancy = input.name_file, input.name_vacancy
    create_csv = CreateCSV(file_name)
    dataframe = create_csv.dataframe
    years = create_csv.all_years

    dataframe["published_at"] = dataframe["published_at"].apply(lambda date: int(date[:4]))
    dataframe['salary'] = dataframe.loc[:, ['salary_from', 'salary_to']].mean(axis=1)

    vacancies = len(dataframe)
    dataframe["count"] = dataframe.groupby("area_name")['area_name'].transform("count")
    dataframe_norm = dataframe[dataframe['count'] >= 0.01 * vacancies]
    all_cities = list(dataframe_norm["area_name"].unique())

    salaries_by_year = {}
    vacancies_by_year = {}
    inp_vacancy_salary = {}
    inp_vacancy_count = {}
    salaries_areas = {}
    vacancies_areas = {}

    for city in all_cities:
        dataframe_s = dataframe_norm[dataframe_norm['area_name'] == city]
        salaries_areas[city] = int(dataframe_s['salary'].mean())
        vacancies_areas[city] = round(len(dataframe_s) / len(dataframe), 4)

    process_executor = futures.ProcessPoolExecutor()
    for year in years:
        args = (vacancy, year)
        list = process_executor.submit(begin_processes, args).result()
        salaries_by_year.update(list[0])
        vacancies_by_year.update(list[1])
        inp_vacancy_salary.update(list[2])
        inp_vacancy_count.update(list[3])

    print("Динамика уровня зарплат по годам:", sort_dictionary(salaries_by_year))
    print("Динамика количества вакансий по годам:", sort_dictionary(vacancies_by_year))
    print("Динамика уровня зарплат по годам для выбранной профессии:", sort_dictionary(inp_vacancy_salary))
    print("Динамика количества вакансий по годам для выбранной профессии:", sort_dictionary(inp_vacancy_count))
    print("Уровень зарплат по городам (в порядке убывания):", sort_dictionary_area(salaries_areas))
    print("Доля вакансий по городам (в порядке убывания):", sort_dictionary_area(vacancies_areas))
