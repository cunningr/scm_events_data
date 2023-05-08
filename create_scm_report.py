#!/usr/bin/env python3

from sdtables.sdtables import SdTables
from datetime import time
from collections import defaultdict

RESULTS_FILE = './gala_swim_times.xlsx'

results_schema = {
    "worksheet": "Sheet1",
    "name": "Table1",
    "properties": {
        "SE Number": {"type": ["string", "null"]},
        "First Name": {"type": ["string", "null"]},
        "Family Name": {"type": ["string", "null"]},
        "Date": {"type": ["string", "null"]},
        "Pool Size": {"type": ["number", "null"]},
        "Swim Distance": {"type": ["number", "null"]},
        "Stroke": {"type": ["number", "null"]},
        "Swim Time": {"type": [time, time(0)]},
        "Split Time 1": {"type": [time, 0]},
        "Split Time 2": {"type": [time, 0]},
        "Split Time 3": {"type": [time, 0]},
        "Split Time 4": {"type": [time, 0]},
        "Position": {"type": ["number", "null"]},
        "Event Number": {"type": ["string", "null"]},
        "Gala ID": {"type": ["string", "null"]},
        "Position": {"type": ["string", "null"]},
        "Round Code": {"type": ["string", "F"]}
    }
}

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
gala_results_wb.load_xlsx_file(RESULTS_FILE)
gala_results_sheets = gala_results_wb.get_all_tables_as_dict()
gala_event_data = gala_results_sheets['Cover']
gala_results_helpers = gala_results_sheets['Helpers']

gala_results_results = dict()
for sheet, tables in gala_results_sheets.items():
    if sheet in ['Fly', 'Back', 'Breast', 'Free', 'Medley']:
        gala_results_results.update(tables)

gala_events_data = {}
for row in gala_results_helpers['events']:
    gala_events_data[row['Event Number']] = row


# Flatten and enrich event data
gala_meta = gala_event_data['main']
data = []
for table, rows in gala_results_results.items():
    if 'EVENT_' in table:
        _, event = table.split('_')
        for row in rows:
            event_metadata = gala_events_data[event]
            row.update({
                "Date": gala_meta[0]['Date'],
                "Pool Size": gala_meta[0]['Pool Size'],
                "Gala ID": gala_meta[0]['Gala ID'],
                "Event Number": event,
                "Swim Distance": event_metadata['Swim Distance'],
                "Stroke": event_metadata['Stroke'],
                "Round Code": "F"
            })
            data.append(row)

scm_updated_wb = SdTables()
scm_updated_wb.add_xlsx_table_from_schema(results_schema['name'], results_schema, data=data, worksheet_name=results_schema['worksheet'], row_offset=0, col_offset=0)
scm_updated_wb.save_xlsx('./scm-results-upload')
