# FreeCodeCamp Scientific Computing with Python - Time Calculator
# Adds a duration time to a start time and returns the result with optional starting day of the week

def add_time(start, duration, starting_day=None):
    # Parse start
    time_part, period = start.split()
    start_hour, start_minute = map(int, time_part.split(":"))

    if period == "PM":
        start_hour += 12

    # Parse duration
    dur_hour, dur_minute = map(int, duration.split(":"))

    # Total minutes and days
    total_minutes = start_minute + dur_minute
    extra_hours = total_minutes // 60
    final_minute = total_minutes % 60

    total_hours = start_hour + dur_hour + extra_hours
    days_later = total_hours // 24
    military_hour = total_hours % 24

    # Determine AM / PM and 12-hour format
    if military_hour == 0:
        final_hour = 12
        final_period = "AM"
    elif military_hour < 12:
        final_hour = military_hour
        final_period = "AM"
    elif military_hour == 12:
        final_hour = 12
        final_period = "PM"
    else:
        final_hour = military_hour - 12
        final_period = "PM"

    new_time = f"{final_hour}:{final_minute:02d} {final_period}"

    # Day of week calculation
    if starting_day:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        start_index = days.index(starting_day.capitalize())
        new_day = days[(start_index + days_later) % 7]
        new_time += f", {new_day}"

    # Days later description
    if days_later == 1:
        new_time += " (next day)"
    elif days_later > 1:
        new_time += f" ({days_later} days later)"

    return new_time

# Tests
print("=== Time Calculator Tests ===")
print("3:00 PM + 3:10            ->", add_time("3:00 PM", "3:10"))
print("11:30 AM + 2:32, Monday   ->", add_time("11:30 AM", "2:32", "Monday"))
print("11:43 AM + 00:20          ->", add_time("11:43 AM", "00:20"))
print("10:10 PM + 3:30           ->", add_time("10:10 PM", "3:30"))
print("11:43 PM + 24:20, tuesday ->", add_time("11:43 PM", "24:20", "tuesday"))
print("6:30 PM + 205:12          ->", add_time("6:30 PM", "205:12"))
