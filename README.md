# EventFeedsLondon

This repository generates automatically updated iCalendar (.ics) event feeds for multiple London areas from a single master event list.

## Features

- Centralized master event data (`data/master_events.txt`) in a pipe-separated format.
- Automatic generation of `.ics` calendar files per area and a combined `AllLondon_Events.ics`.
- Auto-generated plain text event lists for each area.
- GitHub Actions workflow triggers ICS and TXT regeneration on updates to `master_events.txt`.
- Deploys to Netlify to serve calendar feeds publicly.
- Correct HTTP headers set for ICS files via Netlify `_headers` config.

## How it works

1. Add or update events in `data/master_events.txt` with the following pipe-separated format:

