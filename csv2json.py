import sys
import csv
import json

def main(argv):
  csv_file = sys.argv[1]
  read_csv(csv_file)
  
def read_csv(file):
  csv_rows = []
  with open(file) as csvfile:
    reader = csv.DictReader(csvfile)
    title = reader.fieldnames
    for row in reader:
      csv_rows.extend([{title[i]:row[title[i]] for i in range(len(title))}])
    json.dumps(csv_rows)
