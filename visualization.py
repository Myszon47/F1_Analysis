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

#print(race_df.info())

def time_to_seconds(time):
    if isinstance(time, str) and 'N/A' in time:
        return np.nan
    else:  
        time_str = str(time)
        hours, minutes, seconds = time_str.split(':')
        seconds, milliseconds = seconds.split('.')

        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        milliseconds = int(milliseconds)

        total_seconds = (hours * 3600) + (minutes * 60) + seconds
        
        return total_seconds
    
def convert_time(value):
    # Handle special cases (e.g., '+ 2 laps')
    if isinstance(value, str) and 'laps' in value:
        return np.nan
    try:
        return pd.to_timedelta(value)
    except ValueError:
        return np.nan 

# Apply the conversion function to the 'Time/retired' column
race_df['Time/retired'] = race_df['Time/retired'].apply(convert_time)

# Format the 'Time/retired' column to display hours, minutes, seconds, and milliseconds without days
race_df['Time/retired'] = race_df['Time/retired'].apply(lambda x: str(x).split(' ')[-1] if pd.notna(x) else 'N/A')

# Apply the conversion function to the 'Time/retired' column
race_df['Time/retired'] = race_df['Time/retired'].apply(time_to_seconds)


fastest_laps = race_df.groupby('Circuit', as_index=False)['Time/retired'].first()
race_df = pd.merge(race_df, fastest_laps, on='Circuit')

race_df['Time/retired_x'] = race_df.apply(lambda row: row['Time/retired_x'] + row['Time/retired_y'] if row['Time/retired_x'] != row['Time/retired_y'] else row['Time/retired_x'], axis=1) 
#error in Time in Belgium Grand Prix becaues of DNF
race_df.drop(columns=['Time/retired_y'], inplace=True)
race_df.rename(columns={'Time/retired_x' : 'Time/retired'}, inplace=True)

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
driver_standings = race_df.groupby(['Driver', 'Car'], as_index=False)['Pts'].sum()
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

""" plt.figure(figsize=(10,6))
plt.bar(qual_standings['Driver'], qual_standings['Wins'], color=[color_map[x] for x in qual_standings['Car']])
plt.title('Qualifying Wins')
plt.xlabel('Driver')
plt.ylabel('Wins')
plt.show() """

join_standings = pd.merge(driver_standings, team_standings, on='Car')
join_standings.rename(columns={'Pts_x': 'Driver_Points', 'Pts_y':'Team_Points'}, inplace=True)
join_standings['Points_Percentage'] = (join_standings['Driver_Points'] / join_standings['Team_Points']) * 100
pd.options.display.float_format = '{:.2f}'.format
join_standings['Points_Percentage'].replace(np.nan, 0, inplace=True)
#print(join_standings)

""" join_standings['Last_Name'] = join_standings['Driver'].apply(lambda x: x.split()[-1][:3].upper())
small_contribution_threshold = 5

# Create a pivot table for the stacked bar plot
pivot_table = join_standings.pivot(index='Car', columns='Last_Name', values='Points_Percentage')

fig, ax = plt.subplots(figsize=(10, 6))
pivot_table.plot(kind='bar', stacked=True, ax=ax, color='lightblue', edgecolor='black')

# Annotate each segment with the driver's last name
for i in range(len(pivot_table)):
    total = 0  # To keep track of where to place the next label (as each team has stacked percentages)
    for j, last_name in enumerate(pivot_table.columns):
        percentage = pivot_table.iloc[i][last_name]
        if percentage > 0:
            if percentage > small_contribution_threshold:
                # Place the driver's last name in the middle of their segment if it's large enough
                ax.text(i, total + percentage / 2, last_name, ha='center', va='center', fontsize=8, color='black', rotation=90)
            else:
                # Place the driver's last name above the bar if their contribution is too small
                ax.text(i, total + percentage + 1, last_name, ha='center', va='bottom', fontsize=8, color='black', rotation=90)
            total += percentage

# Adding labels and title
plt.title("Percentage of Points Contribution by Drivers Within Teams", fontsize=14)
plt.ylabel("Percentage of Points (%)", fontsize=12)
plt.xlabel("Teams", fontsize=12)

# Removing the default legend as we are displaying driver names directly on the plot
ax.get_legend().remove()

plt.tight_layout()
plt.show() """

week_result_join = pd.merge(race_df[race_df['Pos'] == '1'], qual_df[qual_df['Pos'] == '1'], on='Circuit')
# driver and circuit where driver win qual and race
#print(week_result_join[week_result_join['Driver_x'] == week_result_join['Driver_y']][['Driver_x', 'Circuit']])

# driver and circuit where driver win and get fastest lap
#print(race_df[race_df['Pts'] == 26][['Driver', 'Circuit']])

def seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Example usage:
total_seconds = 3661
formatted_time = seconds_to_hms(total_seconds)
print(formatted_time)  # Output: '01:01:01'



""" plt.figure(figsize=(10,6))
plt.plot(race_df['Circuit'].unique(), race_df[race_df['Pts'] >= 25]['Time/retired'])
plt.title('Race Time')
plt.xlabel('Circuit')
plt.ylabel('Time in seconds')
plt.show()  """

plt.figure(figsize=(10, 6))

# Convert 'Time/retired' column to h:mm:ss format for the legend
time_labels = race_df[race_df['Pts'] >= 25]['Time/retired'].apply(seconds_to_hms)

# Plot each unique circuit with a formatted label
for circuit in race_df['Circuit'].unique():
    circuit_data = race_df[race_df['Circuit'] == circuit]
    if len(circuit_data[circuit_data['Pts'] >= 25]) > 0:
        plt.plot(circuit_data['Circuit'], circuit_data['Time/retired'],
                 label=f"{circuit} ({seconds_to_hms(circuit_data['Time/retired'].iloc[0])})")

plt.title('Race Time')
plt.xlabel('Circuit')
plt.ylabel('Time in seconds')
plt.legend(title='Circuit Time')
plt.show()