import csv
import sys
NUMBER_OF_VARIATIONS = 11
values = []

print(f'Reading {sys.argv[1]}')
with open(sys.argv[1]) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        values.append(list(row))

print(f'Calculating context')
row_count = len(values)
number_of_options = (len(values[0]) - 2)
max_variations = (number_of_options ** row_count)
step = max_variations // NUMBER_OF_VARIATIONS

results = [['VARIABLE', 'UNIT']] + [[row[0], row[1]] for i, row in enumerate(values)]

pos = NUMBER_OF_VARIATIONS // 2

print(f'Preparing Variations')
for i in range(NUMBER_OF_VARIATIONS):
    results[0].append(f'Variation.{i}')
    pos += step
    for r_i in range(row_count):
        results[r_i + 1].append(values[r_i][2 + ((pos // number_of_options**r_i) % number_of_options)])

print(f'Writing {sys.argv[2]}')
with open(sys.argv[2], 'w+') as csvfile:
    csvfile.write('\n'.join((','.join(row) for row in results)))

