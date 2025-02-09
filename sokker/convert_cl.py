import csv
import json
fixtures = []
with open('cl.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    # Iterate through the rows if needed
    round = []
    counter = 1
    for row in csv_reader:
        round.append(row)
        counter += 1
        if counter == 19:
            fixtures.append(round)
            round = []
            counter = 1

with open('cl.json', 'w', encoding='utf-8') as json_file:
    json.dump(fixtures, json_file, ensure_ascii=False, indent=4)



