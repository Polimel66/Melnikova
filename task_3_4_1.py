import math
from statistics import mean
import pandas as pd

pd.set_option("expand_frame_repr", False)
dataframe = pd.read_csv("csv_files/vacancies_dif_currencies.csv")
dataframe_published_at = pd.read_csv("csv_3_3_1.csv")


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


dataframe["salary"] = dataframe.apply(
    lambda row: process_salaries(row["salary_from"], row["salary_to"], row["salary_currency"],
                                 row["published_at"][:7].split("-")), axis=1)
dataframe[:100].to_csv("csv_3_4_1.csv", index=False)
