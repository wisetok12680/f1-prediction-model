import fastf1

schedule_2025 = fastf1.get_event_schedule(2025)

print(schedule_2025[[
    "RoundNumber",
    "EventName",
    "EventDate",
    "Country"
]])
