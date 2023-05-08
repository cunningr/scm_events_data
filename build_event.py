#!/usr/bin/env python3

from sdtables.sdtables import SdTables
from datetime import time
from collections import defaultdict
import re

LANE_COUNT = 4
POOL_SIZE = 20
GALA_TITLE = "POYNTON DIPPERS ANNUAL CLUB CHAMPIONSHIP GALA"
GALA_DATE = "15/10/2022"
GALA_LOCATION = "Poynton Leisure Centre"
GALA_ID = "30D357FC-A9B0-4CF2-9BD6-B459D92995D4"
OUTPUT_FILE = "gala_swim_times"

# # Schema
gala_schema = {
    "description": GALA_TITLE,
    "properties": {
        "Date": {"type": ["string", GALA_DATE]},
        "Location": {"type": ["string", GALA_LOCATION]},
        "Pool Size": {"type": ["number", POOL_SIZE]},
        "Gala ID": {"type": ["number", GALA_ID]}
    },
    "data": [{
        "Date": GALA_DATE,
        "Location": GALA_LOCATION,
        "Pool Size": POOL_SIZE,
        "Gala ID": GALA_ID
    }]
}
heat_schema = {
    "description": "DUMMY",
    "properties": {
        "Heat": {"type": ["number", "null"]},
        "Lane": {"type": ["number", "null"]},
        "SE Number": {"type": ["number", 0]},
        "First Name": {"type": ["string", "null"]},
        "Family Name": {"type": ["string", "null"]},
        "Swim Time": {"type": [time, "null"]},
        "Position": {"type": ["number", "null"]},
        "Split Time 1": {"type": [time, "null"]},
        "Split Time 2": {"type": [time, "null"]},
        "Split Time 3": {"type": [time, "null"]},
        "Split Time 4": {"type": [time, "null"]}
    }
}

def load_event_csv_data(file):
    """
    Returns list(dict()) from CSV file where the first row contains headers (keys)
    """
    with open(file, 'r') as csvfile:
        records = [line.rstrip() for line in csvfile]

    headers = records.pop(0).split(',')

    table = []
    for row in records:
        _r = {headers[i].encode('ascii', 'ignore').decode(): f for i, f in enumerate(row.split(','))}
        table.append(_r)
    
    return table

def enrich_event_data(data):
    """
    For each event, enrich the metadata by parsing the 'Event Name' string
    """
    for _, info in data.items():
        if matches := re.match('(\d+)m (Back|Breast|Fly|Free|Medley) (\w\d+) yr. (Girls|Boys)', info['Event Name']):
            info.update({"Swim Distance": int(matches[1])})
            info.update({"Lengths": int(int(matches[1])/POOL_SIZE)})
            info.update({"Stroke": matches[2]})
            info.update({"Age Group": matches[3]})
            info.update({"Gender": matches[4]})
            if info['Lengths'] % 2 == 0:
                info.update({"Timekeepers": "Deep End"})
            else:
                info.update({"Timekeepers": "Shallow End"})
        else:
            print('WARN - Could not parse event category')


def create_heats(event):
    for heat, i in enumerate(range(0, len(event), LANE_COUNT)):
        for lane, record in enumerate(event[i:i + LANE_COUNT]):
            record.update({"Heat": heat + 1})
            record.update({"Lane": lane + 1})
        # print(i)
        yield event

# Main scripts

# List of each entrant (dict) loaded from SCM event CSV data
event_records = load_event_csv_data('22S.csv')

# Create a dictionary for each event (key) where the value is a dict of metadata 
events_map = {}
for row in event_records:
    events_map[row['Event Number']] = {
        "Event Number": row['Event Number'],
        "Event Name": row['Event Name']
    }
enrich_event_data(events_map)

# Create a new dict of events where each event contains a list of competitors (dict)
# Each competitor is simply extracted from the original event data
events = defaultdict(list)
for competitor in event_records:
    events[competitor['Event Number']].append(competitor)

# Further parse each event adding heats and lanes information
# Create an sdtabels compatible table for each event
events_tables = {}
for id, competitors in events.items():
    # Add heats and lanes
    for event in create_heats(competitors):
        event_name = f'EVENT_{id}'
        events_tables[event_name] = event


# Create a new sdtables workbook
event_wb = SdTables()
event_wb.add_xlsx_table_from_schema("main", gala_schema, data=gala_schema['data'], worksheet_name="Cover")

# Add the events tables using the heat_schema, updating the description
for _table, _rows in events_tables.items():
    # Get the event metadata to create a suitable table label
    _, event_id = _table.split('_')
    event_data = events_map[event_id]
    _label = f"Event: {event_id} | {event_data['Gender']} {event_data['Age Group']}: {event_data['Stroke']} | {event_data['Swim Distance']}m {event_data['Lengths']} Lengths | Timekeepers: {event_data['Timekeepers']}"
    heat_schema['description'] = _label

    # Add the table to the worksheet
    event_wb.add_xlsx_table_from_schema(_table, heat_schema, data=_rows, worksheet_name=event_data['Stroke'])

# Flatten the events_map so that we can add as a tabel
_events_table = [row for _,row in events_map.items()]
event_wb.add_xlsx_table_from_data("events", data=_events_table, worksheet_name="Helpers")

# Create a helpers table with each competitor
competitors = {}
for row in event_records:
    competitors[row['SE Number']] = {"SE Number": row['SE Number'], "First Name": row['First Name'], "Family Name": row['Family Name']}
    # competitors.append({"SE Number": row['SE Number'], "First Name": row['First Name'], "Family Name": row['Family Name']})
event_wb.add_xlsx_table_from_data("competitors", data=[v for _,v in competitors.items()], worksheet_name="Helpers")

# Finally save our openpyexcel workbook
event_wb.save_xlsx(OUTPUT_FILE)
