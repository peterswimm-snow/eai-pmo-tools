"""One module per report generator.

Each module assembles cached data (see ../cache.py) into the section
structure its sibling spec in reporting/generators/*.md defines. None of
these render documents themselves — see ../render.py for why.

`core_team_action` is the most complete starting point: every ServiceNow
source it needs is confirmed (see data_sources.CONFIRMED_COMMANDS), so it
has no placeholder-handling logic to get right before it's useful. The
other four modules are intentionally thinner stubs — build them out
following the same shape once their underlying TBD data sources
(data_sources.QUERY_CATEGORIES) are confirmed on the real instance.
"""
