#!/usr/bin/env python3

from sdtables.sdtables import SdTables
from datetime import time
from collections import defaultdict

def update_result(record, results_tables):
    event = record['Event Number']
    swimmer_id = record['Swimmer ID']
    swimmer_name = record['Swimmer']
    event_results = results_tables[f'EVENT_{event}']
    result = [r for r in event_results if swimmer_id in r['id']]
    if len(result) > 1:
        print(f"Error: Found duplicate results in event {event} for {swimmer_name} with scm id {swimmer_id}")
    elif result[0]['result'] is None:
        record['Result'] = time(0)
    else:
        print(result[0]['result'])
        record['Result'] = result[0]['result']

gala_results_wb = SdTables()
gala_results_wb.load_xlsx_file('./gala_results.xlsx')

scm_results_wb = SdTables()
scm_results_wb.load_xlsx_file('./22S-Results.xlsx')
scm_sheets = scm_results_wb.get_all_tables_as_dict()
# Swimmer ID
# Result

scm_results_table = scm_sheets['Sheet1']['Table1']

sheets = gala_results_wb.get_all_tables_as_dict()
results_tables = sheets['All Heats']

for row in scm_results_table:
    update_result(row, results_tables)

results_schema = {
    "worksheet": "Sheet1",
    "name": "Table1",
    "description": "Lookup table for organisers and timekeepers",
    "properties": {
        "Event Number": {"type": ["string", "null"]},
        "Event Name": {"type": ["string", "null"]},
        "Swimmer ID": {"type": ["string", "null"]},
        "Swimmer": {"type": ["string", "null"]},
        "DOB": {"type": ["string", "null"]},
        "Result": {"type": [time, time(0)]},
        "Position": {"type": ["string", "null"]},
        "Disqualified": {"type": ["string", "null"]},
        "Disqualified Reason": {"type": ["string", "null"]},
        "Round": {"type": ["string", "null"]}

    },
}

scm_updated_wb = SdTables()
scm_updated_wb.add_xlsx_table_from_schema(results_schema['name'], results_schema, data=scm_results_table, worksheet_name=results_schema['worksheet'])
# scm_updated_wb.add_xlsx_table_from_data("Table1", scm_results_table, worksheet_name="Sheet1")
scm_updated_wb.save_xlsx('./22S-Results_new')

# for name, table in sheets['All Heats'].items():
#     _, event = name.split('_')
#     print(f'*****{event}')
#     for row in table:
#         row.update({'Event Number': event})
#         print(row)
