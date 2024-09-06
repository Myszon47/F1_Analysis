#import libraries
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

#change pd options to see a whole DataFrame
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Define the base URL for the F1 results
URL = 'https://www.formula1.com/en/results/2024/races/1229/bahrain/race-result'

# Fetch the main results page to scrape all race URLs
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

# Scrape URLs for each race (race results)
race_titles_search = soup.find_all(attrs={"class": "block", "href": re.compile("^/en/results/2024/races/12[0-9]*/[a-z]*[-]*[a-z]*/race-result")})
race_URLs = [x['href'] for x in race_titles_search]
race_URLs = race_URLs[0:-1]
race_titles = [x.get_text() for x in race_titles_search]
race_titles.pop(len(race_titles)-1)

# Create qualifying URLs by replacing 'race-result' with 'qualifying'
qualifying_URLs = [url.replace("race-result", "qualifying") for url in race_URLs]

# DataFrame to store race and qualifying results
race_df = pd.DataFrame()
qualifying_df = pd.DataFrame()

def get_results(url, race_number, race_titles):
    """
    Function to scrape race or qualifying results for a specific race.
    
    Parameters:
    - url: the full URL to the results page
    - race_number: the index of the race
    - race_titles: list of race names/titles

    Returns:
    - A DataFrame containing the results for that race or qualifying session.
    """
    # Fetch the results page
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    race_title = race_titles[race_number]	# Get race title for the given race number

    try:
        # Get the results table
        race_results_table = soup.find(class_ = "f1-table")
        
        # Get headers
        race_headers_search = race_results_table.find_all('th')
        race_headers = [x.get_text() for x in race_headers_search]
        race_headers.append('Circuit')	# Add an extra column for circuit name

        # Get all the result rows
        race_results_search = race_results_table.find_all(class_ = 'f1-text')
        race_results = [x.get_text() for x in race_results_search]
        
        # Organize results into rows, matching the header structure
        race_results = race_results[len(race_headers)-1:len(race_results)]
        race_results_row = []
        for x in range(0,len(race_results)-5,len(race_headers)-1):
            race_results_row += [race_results[x:x+len(race_headers)-1]]

        # Create DataFrame for this race
        df = pd.DataFrame(columns = race_headers)
        for row in race_results_row:
            df_length = len(df)
            df.loc[df_length] = row + [race_title]

        # Clean up the data
        df.drop(columns=['No', 'Laps'], axis=0, inplace=True)	# Drop unwanted columns
        df['Driver'] = df['Driver'].str[:-3]	# Clean driver names
        
        return df
    except AttributeError:  # This handles cases where the race hasn't taken place yet
        print(f"Race '{race_title}' has not yet taken place.")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Loop over race URLs and qualifying URLs to get results
race_dfs = []
qualifying_dfs = []

for race_number in range(len(race_URLs)-1):
    race_full_url = 'https://www.formula1.com' + race_URLs[race_number]
    qualifying_full_url = 'https://www.formula1.com' + qualifying_URLs[race_number]
    
    # Append the race and qualifying data to the lists
    race_dfs.append(get_results(race_full_url, race_number, race_titles))
    qualifying_dfs.append(get_results(qualifying_full_url, race_number, race_titles))

# Concatenate all the race and qualifying results into one DataFrame each
if race_dfs:
    race_df = pd.concat(race_dfs, ignore_index=True)

if qualifying_dfs:
    qualifying_df = pd.concat(qualifying_dfs, ignore_index=True)

# Save results to Excel file
with pd.ExcelWriter('f12024_results.xlsx', engine='xlsxwriter') as writer:
    race_df.to_excel(writer, sheet_name='race_results', index=False)
    qualifying_df.to_excel(writer, sheet_name='qualifying_results', index=False)

print("Results have been successfully saved to 'f12024_results.xlsx'.")