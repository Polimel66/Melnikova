import pandas as pd
import requests


def make_urls():
    urls = []
    for i in range(1, 23):
        if i == 9:
            urls.append(
                f"https://api.hh.ru/vacancies?date_from=2022-12-19T0{i}:00:00&date_to=2022-12-19T{i + 1}:00:00&specialization=1&")
        elif 1 <= i <= 8:
            urls.append(
                f"https://api.hh.ru/vacancies?date_from=2022-12-19T0{i}:00:00&date_to=2022-12-19T0{i + 1}:00:00&specialization=1&")
        else:
            urls.append(
                f"https://api.hh.ru/vacancies?date_from=2022-12-19T{i}:00:00&date_to=2022-12-19T{i + 1}:00:00&specialization=1&")
    return urls


pd.set_option("expand_frame_repr", False)
urls = make_urls()

dataframe = pd.DataFrame(columns=["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"])
for url in urls:
    all_pages = requests.get(url).json()
    for page in range(all_pages["pages"]):
        params = {'page': page}
        response = requests.get(url, params=params)
        json = requests.get(url, params=params).json()
        items = json["items"]
        for vacancy in items:
            try:
                dataframe.loc[len(dataframe)] = [vacancy["name"], vacancy["salary"]["from"], vacancy["salary"]["to"],
                                                 vacancy["salary"]["currency"], vacancy["area"]["name"],
                                                 vacancy["published_at"]]
            except TypeError:
                continue
dataframe.to_csv("csv_3_3_3.csv", index=False)
print(dataframe)
