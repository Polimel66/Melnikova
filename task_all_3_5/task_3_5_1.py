import pandas as pd
import sqlite3

connection = sqlite3.connect('task_3_5.sqlite')
cursor = connection.cursor()
dataframe = pd.read_csv('csv_currencies.csv')
dataframe = dataframe.to_sql('currencies', connection, if_exists='replace', index=False)
connection.commit()
