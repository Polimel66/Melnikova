import pandas as pd

name_file = "csv_files/vacancies_by_year.csv"
dataframe = pd.read_csv(name_file)
dataframe["years"] = dataframe["published_at"].apply(lambda date: int(date[:4]))
all_years = list(dataframe["years"].unique())
for year in all_years:
    data = dataframe[dataframe["years"] == year]
    data.iloc[:, :6].to_csv(f"created_csv_by_year\\chunk_{year}.csv", index=False)
