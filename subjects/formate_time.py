def format_time(time_str):
    # Split the input time string
    hours, minutes = map(int, time_str.split(':'))

    # Determine if it's a.m. or p.m.
    if hours >= 12:
        period = 'p.m.'
        if hours > 12:
            hours -= 12  # Convert to 12-hour format
    else:
        period = 'a.m.'
        if hours == 0:
            hours = 12  # Midnight case

    # Format the output string
    return f"{hours:02}:{minutes:02} {period}"
