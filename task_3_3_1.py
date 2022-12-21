import requests
import pandas as pd

pd.set_option('expand_frame_repr', False)
dataframe = pd.read_csv('csv_files/vacancies_dif_currencies.csv')
dataframe['published'] = pd.to_datetime(dataframe['published_at'], format='%Y-%m-%dT%H:%M:%S%z', utc=True)
sorted_data = dataframe.sort_values(by='published').reset_index()
all_months = list(sorted_data.published.dt.strftime('%m/%Y').unique())
number_uses = dataframe.groupby('salary_currency')['salary_currency'].count()
dict = number_uses[number_uses > 5000].to_dict()
print(dict)
str_currencies = ['BYR', 'EUR', 'KZT', 'UAH', 'USD']
second_data = pd.DataFrame(columns=['date'] + str_currencies)


def make_loc(currency_str):
    return float(
        second_currencies.loc[second_currencies['CharCode'] == currency_str]['Value'].values[0].replace(',', '.')) / \
           (second_currencies.loc[second_currencies['CharCode'] == currency_str]['Nominal'].values[0])


for i in range(0, len(all_months)):
    url = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{all_months[i]}d=1'
    response = requests.get(url)
    currencies = pd.read_xml(response.text)
    second_currencies = currencies.loc[currencies['CharCode'].isin(['BYN'] + str_currencies)]
    EUR = make_loc('EUR')
    BYR = float(
        second_currencies.loc[second_currencies['CharCode'].isin(['BYR', 'BYN'])]['Value'].values[0].replace(',',
                                                                                                             '.')) / \
          (second_currencies.loc[second_currencies['CharCode'].isin(['BYR', 'BYN'])]['Nominal'].values[0])
    UAH = make_loc('UAH')
    KZT = make_loc('KZT')
    USD = make_loc('USD')
    second_data.loc[i] = [f'{all_months[i][3:]}-{all_months[i][:2]}', BYR, EUR, KZT, UAH, USD]
second_data.to_csv('csv_3_3_1.csv')
print(second_data.head())
