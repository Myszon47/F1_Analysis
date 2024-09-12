import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

file_path = 'f12024_results.xlsx'

if os.path.exists(file_path):
	race_df = pd.read_excel(file_path, sheet_name='race_results')
	qual_df = pd.read_excel(file_path, sheet_name='qualifying_results')
else:
	print("File doesn't exist")

""" plt.figure(figsize=(10, 6))
race_df['Position'] = pd.to_numeric(race_df['Pos'], errors='coerce')
plt.bar(race_df['Driver'], race_df['Position'])
plt.xticks(rotation=90)
plt.title('Driver Positions in the Race')
plt.xlabel('Driver')
plt.ylabel('Position')
plt.tight_layout()
plt.show() """

#print(race_df.info())

#print(race_df['Car'].unique())
color_map = {
    'Red Bull Racing Honda RBPT': 'navy',
    'Ferrari': 'red',
    'Mercedes': 'turquoise',
    'McLaren Mercedes': 'orange',
    'Aston Martin Aramco Mercedes': 'darkgreen',
    'Kick Sauber Ferrari': 'black',
    'Haas Ferrari': 'lightgrey',
    'RB Honda RBPT': 'lightblue',
    'Williams Mercedes': 'blue',
    'Alpine Renault': 'darkslategrey'    
}
driver_standings = race_df.groupby('Driver', as_index=False)['Pts'].sum()
driver_standings = driver_standings.sort_values(by='Pts', ascending=False)
driver_standings.reset_index(drop=True, inplace=True)
#print(driver_standings)

team_standings = race_df.groupby('Car', as_index=False)['Pts'].sum()
team_standings = team_standings.sort_values(by='Pts', ascending=False)
team_standings.reset_index(drop=True, inplace=True)
#print(team_standings)

""" plt.figure(figsize=(10,6))
plt.bar(team_standings['Car'], team_standings['Pts'], color=[color_map[x] for x in team_standings['Car']])
plt.title('Team Standings')
plt.xlabel('Team')
plt.ylabel('Points')
plt.show() 

plt.figure(figsize=(10,6))
plt.bar(driver_standings['Driver'], driver_standings['Pts'], color=[color_map[x] for x in driver_standings['Car']])
plt.title('Driver Standings')
plt.xlabel('Driver')
plt.ylabel('Points')
plt.show()  """

qual_standings = qual_df[qual_df['Pos'] == '1']
qual_standings = qual_standings.groupby(['Driver', 'Car'], as_index=False).size()
qual_standings.rename(columns={'size' : 'Wins'}, inplace=True)
qual_standings = qual_standings.sort_values(by='Wins', ascending=False)
#print(qual_standings)

plt.figure(figsize=(10,6))
plt.bar(qual_standings['Driver'], qual_standings['Wins'], color=[color_map[x] for x in qual_standings['Car']])
plt.title('Qualifying Wins')
plt.xlabel('Driver')
plt.ylabel('Wins')
plt.show()
