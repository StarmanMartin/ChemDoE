import json  # Import JSON module to read and write JSON files
import random
import sys  # Import sys to access command-line arguments

# Define the number of variations to generate
NUMBER_OF_VARIATIONS = 11

print(f'Generating {NUMBER_OF_VARIATIONS} random  variables')

# Read the input JSON file passed as the first command-line argument
print(f'Reading {sys.argv[1]}')
with open(sys.argv[1]) as jsonfile:
    values = json.loads(jsonfile.read())  # Load JSON content into a dictionary

# Calculate context-related values
print(f'Calculating context')
row_count = len(values)  # Total number of keys (variables) in the JSON data
number_of_options = len(values[list(values.keys())[0]]) - 1  # Number of options per variable (excluding unit)
print('Number of variables: ' + str(row_count))
print('Number of values per row: ' + str(number_of_options))
# Initialize results dictionary with VARIABLE and UNIT lists
results = {'VARIABLE': [], 'UNIT': []}

# Populate VARIABLE and UNIT lists with keys and corresponding unit values
for r_i, r_v in values.items():
    results['VARIABLE'].append(r_i)  # Store the variable name (key)
    results['UNIT'].append(r_v[0])  # Store the unit (first element of the value list)



# Generate variations and store them in the results dictionary
print(f'Preparing Variations')
for i in range(NUMBER_OF_VARIATIONS):
    results[f'Variation.{i}'] = []  # Initialize a new list for each variation
    for r_i, r_v in enumerate(values.values()):
        # Select a variation value based on computed index
        results[f'Variation.{i}'].append(random.choice(r_v[1:]))

# Write the results to the output JSON file
print(f'Writing {sys.argv[2]}')
with open(sys.argv[2], 'w+') as json_file:
    json_file.write(json.dumps(results, indent=4))  # Convert dictionary to JSON and write to file
