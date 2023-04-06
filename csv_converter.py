import pandas as pd

# Load the CSV file
df = pd.read_csv('sheep_positions_1.csv', header=None)

# Extract the X and Y coordinates into separate columns
df[['X', 'Y']] = pd.DataFrame(df[0].tolist(), index=df.index)

# Save the modified CSV file
df.to_csv('sheep_positions_mod.csv', index=False)