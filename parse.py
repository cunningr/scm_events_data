#!/usr/bin/env python3

from sdtables.sdtables import SdTables
from datetime import time
from collections import defaultdict

tables = SdTables()
tables.load_xlsx_file('./22S-Results.xlsx')

LANE_COUNT = 4

def check_time_format(idx, row):
    for key in row.keys():
        if "Time" in key:
            if not isinstance(row[key], time) and row[key] is not None:
                print(f'row {idx + 1} column: "{key}" contains errors: {row[key]}')

def create_heats(event):
    for heat, i in enumerate(range(0, len(event), LANE_COUNT)):
        for lane, record in enumerate(event[i:i + LANE_COUNT]):
            record.update({"heat": heat + 1})
            record.update({"lane": lane + 1})
        # print(i)
        yield event

# Create a dictionary of Event ID to name
events_map = {}
for _, rows in tables.get_table_as_dict('Table1').items():
    for row in rows:
        events_map[row['Event Number']] = row['Event Name']


# Create a dictionary of Event ID to name
_table = []
for _, rows in tables.get_table_as_dict('Table1').items():
    for row in rows:
        _table.append({"id": row['Swimmer ID'], "name": row['Swimmer']})
        competitors_table = list({v['id']:v for v in _table}.values())

# For each event, add the list of competitors
events = defaultdict(list)
for _, rows in tables.get_table_as_dict('Table1').items():
    for row in rows:
        competitor = {
            "id": row['Swimmer ID'],
            "name": row['Swimmer'],
            "result": ""
        }
        events[row['Event Number']].append(competitor)


# Iterate each event and label the heats.
# Each heat is a list of competitors by lane
# These will become individual tables
heats = {}
for id, competitors in events.items():
    # Add heats and lanes
    for event in create_heats(competitors):
        event_name = f'EVENT_{id}'
        heats[event_name] = event


# Schema
heat_schema = {
    "description": "SOMETHING",
    "properties": {
        "heat": {"type": ["number", "null"]},
        "lane": {"type": ["number", "null"]},
        "id": {"type": ["string", "null"]},
        "name": {"type": ["string", "null"]},
        "result": {"type": [time, 0]}
    }
}
time_keepers = {
    "worksheet": "helpers",
    "name": "time_keepers",
    "description": "Lookup table for organisers and timekeepers",
    "properties": {
        "Distance": {"type": ["string", "null"]},
        "#Lengths": {"type": ["number", "null"]},
        "Timekeepers": {"type": ["string", "null"]}
    },
    "seed": [
        {"Distance": "20m", "#Lengths": 1, "Timekeepers": "Shallow End"},
        {"Distance": "40m", "#Lengths": 2, "Timekeepers": "Deep End"},
        {"Distance": "60m", "#Lengths": 3, "Timekeepers": "Shallow End"},
        {"Distance": "80m", "#Lengths": 4, "Timekeepers": "Deep End"}
    ]
}
competitors = {
    "worksheet": "helpers",
    "name": "competitors",
    "description": "List of competitors with SCM GUID",
    "properties": {
        "id": {"type": ["string", "null"]},
        "name": {"type": ["string", "null"]}
    }
}

# Create tables!
tables = SdTables()
worksheet_name = "testing"
for id, heat in heats.items():
    # print(id)
    _, _event =  id.split('_')
    description = f"Event: {_event} - {events_map[_event]}"
    heat_schema['description'] = description
    # print(f"Event: {_event}, Heat: {_heat} - {events_map[_event]}")
    # tables.add_xlsx_table_from_data(id, heat, worksheet_name=worksheet_name)
    tables.add_xlsx_table_from_schema(id, heat_schema, data=heat, worksheet_name='All Heats')
    # print(heat)
    # for row in heat:
        # print(row)

tables.add_xlsx_table_from_schema(time_keepers['name'], time_keepers, data=time_keepers['seed'], worksheet_name=time_keepers['worksheet'])
tables.add_xlsx_table_from_schema(competitors['name'], competitors, data=competitors_table, worksheet_name=competitors['worksheet'])
tables.save_xlsx('gala_results')