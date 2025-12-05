import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# Load and prepare data
gdp = pd.read_csv("GDP_Per_Capita.csv", header=0)
gdp = gdp[['Reference area', 'TIME_PERIOD', 'OBS_VALUE']]
gdp = gdp.rename(columns={
    'Reference area': 'Country',
    'TIME_PERIOD': 'Time',
    'OBS_VALUE': 'Observation value'
})

# Filter for selected countries - Major economies for macroeconomic analysis
Countries = ['United States', 'Germany', 'Japan', 
             'United Kingdom']
gdp = gdp[gdp['Country'].isin(Countries)]

# Convert Time to datetime and sort
gdp['Time'] = pd.to_datetime(gdp['Time'])
gdp = gdp.sort_values(by='Time')

# Resample by country (groupby + resample)
print(gdp)

txt = "Data Source: OECD GDP Per Capita Dataset"

# Create professional figure
fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
# Define professional color palette - expanded for more countries
colors = {
    'United States': '#7f1718',
    'Germany': '#6fa6ff',
    'Japan': '#003e8d',
    'United Kingdom': '#234a00',
}

# Plot each country with enhanced styling
for country, group in gdp.groupby('Country'):
    ax.plot(group['Time'], group['Observation value'], 
            label=country, 
            color=colors.get(country, '#333333'),
            linewidth=2.5,
            marker='o',
            markersize=4,
            alpha=0.9)

# Styling
ax.set_title('Real GDP Per Capita', 
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=12, fontweight='semibold')
ax.set_ylabel('Real GDP Per Capita ($)', fontsize=12, fontweight='semibold')

ax.xaxis.set_major_locator(mpl.dates.YearLocator())
ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y'))# Improve legend
ax.legend(title='Economy', 
          title_fontsize=11,
          fontsize=10,
          loc='best',
          frameon=True,
          shadow=True,
          fancybox=True)

fig.text(0, 0.01, txt, ha='left', fontsize=9, color='#555555')
# Grid styling
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
ax.set_axisbelow(True)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Add subtle background
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('white')

# Adjust spines
for spine in ax.spines.values():
    spine.set_edgecolor('#cccccc')
    spine.set_linewidth(1)

# Tight layout
plt.tight_layout()

# Save as high-resolution image for PowerPoint
plt.savefig('gdp_outlook_professional.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

plt.show()

print("Professional chart saved as 'gdp_outlook_professional.png'")
