import csv  # Import the CSV module to read and write CSV files
import random
import sys  # Import sys to access command-line arguments

# Define the number of variations to generate
NUMBER_OF_VARIATIONS = 11

print(f'Generating {NUMBER_OF_VARIATIONS} random  variables')

# List to store the CSV data
values = []

# Read the input CSV file passed as the first command-line argument
print(f'Reading {sys.argv[1]}')
with open(sys.argv[1]) as csvfile:
    reader = csv.reader(csvfile)  # Create a CSV reader object
    for row in reader:
        values.append(list(row))  # Convert each row to a list and store it

# Calculate context-related values
print(f'Calculating context')
row_count = len(values)  # Total number of rows in the CSV
number_of_options = len(values[0]) - 2  # Number of available options per column (excluding first two columns)

print('Number of variables: ' + str(row_count))
print('Number of values per row: ' + str(number_of_options))

# Initialize results dictionary with VARIABLE and UNIT lists
# Initialize results list with headers and units
# [
# [VARIABLE, UNIT, Variation.1, Variation.2, ...]   First Row
# [S:xx, mol, 0.1, 0.2, ...]                        Second Row
# ...                                               ... nth row
# ]
results = [['VARIABLE', 'UNIT']] + [[row[0], row[1]] for i, row in enumerate(values)]


# Generate variations and store them in the results list
print(f'Preparing Variations')
for i in range(NUMBER_OF_VARIATIONS):
    results[0].append(f'Variation.{i}')  # Append variation headers
    for r_i in range(row_count):
        # Select a variation value based on a random choice
        results[r_i + 1].append(random.choice(values[r_i][2:]))

# Write the results to the output CSV file
print(f'Writing {sys.argv[2]}')
with open(sys.argv[2], 'w+') as csvfile:
    csvfile.write('\n'.join((','.join(row) for row in results)))  # Format and write CSV content
