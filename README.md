# scm_events_data
Tools for processing SCM Events data

Export events pack from SCM and extract the entrants CSV file.

```
./build_event.py
```

Complete the times and race results in the newly generated `gala_results.xlsx` where you will find a table for each event and some "Helper" tables with event and competitor information.

Once you have all the results in the event tables, run:

```
./create_scm_report.py
```

This will generate a new workbook with a single sheet containing all the swim times for upload to SCM.

Note: Although the timedata should be valid, you will need to highlight all the time fields, 'right-click' and set "Format-Cells" => `mm.ss.00`
