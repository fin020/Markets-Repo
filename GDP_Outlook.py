import pandas as pd 
from pandas import DataFrame, Series
import requests 
from io import StringIO
import numpy as np
import matplotlib.pyplot as plt

#Define API query URL (CSV)


# url = 'https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA_EXPENDITURE_GROWTH_OECD,/Q..AUS+AUT+BEL+CAN+CHL+COL+CRI+CZE+DNK+EST+FIN+FRA+DEU+GRC+HUN+ISL+IRL+ISR+ITA+JPN+KOR+LVA+LTU+LUX+MEX+NLD+NZL+NOR+POL+PRT+SVK+SVN+ESP+SWE+CHE+TUR+GBR+USA+G7+G20+EA20+EU27_2020+OECD+OECDE+ARG+BRA+CHN+IND+IDN+SAU+ZAF+USMCA.S1..B1GQ......G1.?startPeriod=2023-Q3&endPeriod=2025-Q3&format=csvfilewithlabels'
# response = requests.get(url)
# df = pd.read_csv(StringIO(response.text))
# df.to_csv('output.csv')
# print(df.columns.tolist())

df = pd.read_csv('output.csv', header=0)

print(df[['Reference area','TIME_PERIOD','OBS_VALUE']])
df = df[['Reference area','TIME_PERIOD','OBS_VALUE']]
df = df.rename(columns={
    'Reference area' : 'Country',
    'TIME_PERIOD' : 'Time',
    'OBS_VALUE': 'Observation value'
})


fig = plt.figure(figsize=(12,8))

for country, group in df.groupby('Country'):
    plt.plot(group['Time'], group['Observation value'], marker='o', label=country)
    
plt.title('Real GDP change over time by OECD Country')
plt.xlabel('Time Period')
plt.ylabel('GDP Change')
plt.legend(title='Country')
plt.grid(True)
plt.tight_layout()
plt.show()

plt.clf()

Countries = ['OECD Europe','United Kingdom','United States']
df = df[df['Country'].isin(Countries)]
df = df.sort_values(by='Time')

fig = plt.Figure()
plt.style.use('ggplot')
for country, group in df.groupby('Country'):
    plt.plot(group['Time'], group['Observation value'], marker='o', label=country)
    
plt.title('Real GDP change over time by OECD Country')
plt.xlabel('Time Period')
plt.ylabel('GDP Change')
plt.legend(title='Country')
plt.grid(True)
plt.tight_layout()
plt.show()
