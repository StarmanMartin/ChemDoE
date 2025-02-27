import json
import sys
NUMBER_OF_VARIATIONS = 11


print(f'Reading {sys.argv[1]}')
with open(sys.argv[1]) as jsonfile:
    values = json.loads(jsonfile.read())

print(f'Calculating context')
row_count = len(values)
number_of_options = len(values[list(values.keys())[0]]) - 1
max_variations = (number_of_options ** row_count)
step = max_variations // NUMBER_OF_VARIATIONS

results = {'VARIABLE': [], 'UNIT': []}

for r_i, r_v in values.items():
    results['VARIABLE'].append(r_i)
    results['UNIT'].append(r_v[0])

pos = NUMBER_OF_VARIATIONS // 2

print(f'Preparing Variations')
for i in range(NUMBER_OF_VARIATIONS):
    results[f'Variation.{i}'] = []
    pos += step
    for r_i, r_v in enumerate(values.values()):
        results[f'Variation.{i}'].append(r_v[1 + ((pos // number_of_options**r_i) % number_of_options)])

print(f'Writing {sys.argv[2]}')
with open(sys.argv[2], 'w+') as json_file:
    json_file.write(json.dumps(results, indent=4))



