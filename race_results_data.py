import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


URL = 'https://www.formula1.com/en/results/2024/races/1229/bahrain/race-result'

page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

race_titles_search = soup.find_all(attrs={"class": "block", "href": re.compile("^/en/results/2024/races/12[0-9]*/[a-z]*[-]*[a-z]*/race-result")})

URLs = [x['href'] for x in race_titles_search]
URLs = URLs[0:-1]

race_titles = [x.get_text() for x in race_titles_search]
race_titles.pop(len(race_titles)-1)

race_df = pd.DataFrame()


def get_results(url):

	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")

	race_title = race_titles.pop(0)

	try:
		race_results_table = soup.find(class_ = "f1-table")

		race_headers_search = race_results_table.find_all('th')
		race_headers = [x.get_text() for x in race_headers_search]
		race_headers.append('Circuit')

		race_results_search = race_results_table.find_all(class_ = 'f1-text')
		race_results = [x.get_text() for x in race_results_search]
		race_results = race_results[7:len(race_results)-1]
		race_results_row = []
		for x in range(0,len(race_results)-5,7):
			race_results_row += [race_results[x:x+7]]

		df = pd.DataFrame(columns = race_headers)
		for row in race_results_row:
			df_length = len(df)
			df.loc[df_length] = row + [race_title]

		df.drop(columns=['No', 'Laps'], axis=0, inplace=True)
		df['Driver'] = df['Driver'].str[:-3]
		
		return df
	except:
		print("The race has not yet taken place")

for url in URLs:
	race_df = pd.concat([race_df, get_results('https://www.formula1.com' + url)])


race_df.reset_index(drop=True, inplace=True)
print(race_df)