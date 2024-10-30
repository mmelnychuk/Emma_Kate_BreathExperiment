# plot sniff data from a data file from Pauls student experiment

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('subject_data/mi/MW_sniff.csv')

# Plot the 'Temperature' column
df['Nasal Pressure'].plot()

# Show the plot
plt.show()