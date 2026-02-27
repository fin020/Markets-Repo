import pandas as pd
import matplotlib.pyplot as plt

# Load and prepare data
Japan = pd.read_csv("Japan_Inflation.csv", header=0)
inflation = pd.read_csv("inflation_G7.csv", header=0)

inflation = pd.concat([inflation, Japan], ignore_index=True, axis=0)
inflation = inflation[['Reference area', 'TIME_PERIOD', 'OBS_VALUE']]
inflation = inflation.rename(columns={
    'Reference area': 'Country',
    'TIME_PERIOD': 'Time',
    'OBS_VALUE': 'Inflation rate (%)'
})

# Filter for selected countries - Major economies for macroeconomic analysis
Countries = ['United States', 'Germany', 'Japan', 
             'United Kingdom']
inflation = inflation[inflation['Country'].isin(Countries)]

# Convert Time to datetime and sort
inflation['Time'] = pd.to_datetime(inflation['Time'])
inflation = inflation.sort_values(by='Time')

# Resample by country (groupby + resample)
inflation = inflation.set_index('Time')
inflation = inflation.groupby('Country')['Inflation rate (%)'].resample('Y').mean().reset_index()


inflation_rate = inflation.copy()
inflation_rate['Inflation rate (%)'] = inflation.groupby("Country")['Inflation rate (%)'].pct_change() * 100


print(inflation.groupby('Country').describe())

# Create professional figure
fig, ax = plt.subplots(figsize=(12, 7), dpi=150)

# Professional color palette (matches GDP chart so visuals are consistent across report)
colors = {
    'United States': '#7f1718',
    'Germany': '#6fa6ff',
    'Japan': '#003e8d',
    'United Kingdom': '#234a00'
}

# Plot each country
for country, group in inflation_rate.groupby('Country'):
    ax.plot(group['Time'], group['Inflation rate (%)'], 
            label=country,
            color=colors.get(country, '#333333'),
            linewidth=2.5,
            marker='o',
            markersize=4,
            alpha=0.9)

# Styling & labels
ax.set_title('Inflation Trends: Key Global Economies (CPI, %)', 
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=12, fontweight='semibold')
ax.set_ylabel('Inflation Rate (%)', fontsize=12, fontweight='semibold')

# Legend styling
ax.legend(title='Economy',
          title_fontsize=11,
          fontsize=10,
          loc='best',
          frameon=True,
          shadow=True,
          fancybox=True)

# Grid + background
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
ax.set_axisbelow(True)
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('white')

# Adjust axes spines
for spine in ax.spines.values():
    spine.set_edgecolor('#cccccc')
    spine.set_linewidth(1)

# Rotate x-axis labels for readability
plt.xticks(rotation=45, ha='right')

# Tight layout
plt.tight_layout()

# Save high-resolution
plt.savefig('inflation_outlook_professional.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

plt.show()

print("Professional inflation chart saved as 'inflation_outlook_professional.png'")
