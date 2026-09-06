#!/usr/bin/env python3
"""Reset OpenClaw crash-loop breaker and clean sessions.json migration."""
import sqlite3, os, sys

db = '/home/saber/.openclaw/state/openclaw.sqlite'
conn = sqlite3.connect(db)

# Reset crash-loop breaker
n = conn.execute('''
    UPDATE gateway_boot_lifecycle
    SET outcome = "clean_stop", completed_at_ms = started_at_ms + 100
    WHERE outcome = "startup_failed"
''').rowcount
conn.commit()
print(f'Reset {n} failed boot record(s)')

# Show outcomes
outcomes = conn.execute('SELECT outcome, COUNT(*) FROM gateway_boot_lifecycle GROUP BY outcome').fetchall()
print('Outcomes:', outcomes)
conn.close()

# Handle sessions.json migration
sessions = '/home/saber/.openclaw/agents/main/sessions/sessions.json'
if os.path.exists(sessions):
    bak = sessions + '.bak'
    os.rename(sessions, bak)
    print(f'Renamed sessions.json -> sessions.json.bak')
else:
    print('sessions.json not found (ok)')

print('Done.')
