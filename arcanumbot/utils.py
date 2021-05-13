from typing import Union


def detailed_human_time(input_seconds: Union[float, int]):
    # drop nanoseconds
    input_seconds = int(input_seconds)
    minutes, seconds = divmod(input_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365)

    msgs = []
    if years:
        msgs.append(f"{years} year(s)")
    if minutes:
        msgs.append(f"{minutes} minute(s)")
    if days:
        msgs.append(f"{days} day(s)")
    if hours:
        msgs.append(f"{hours} hour(s)")
    if seconds:
        msgs.append(f"{seconds} second(s)")

    if not msgs:
        msgs.append(f"0 second(s)")

    return ", ".join(msgs)