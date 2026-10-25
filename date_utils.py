from datetime import datetime
from email.utils import parsedate_to_datetime


def normalise_date(date_string):
    """
    Convert source dates to ISO format (YYYY-MM-DD).

    Returns:
        (normalised_date, precision)
    """

    # Notion: 2026-05-13
    try:
        date = datetime.strptime(date_string, "%Y-%m-%d")
        return date.strftime("%Y-%m-%d"), "day"
    except ValueError:
        pass

    # monday.com: May 25, 2026
    try:
        date = datetime.strptime(date_string, "%B %d, %Y")
        return date.strftime("%Y-%m-%d"), "day"
    except ValueError:
        pass

    # Asana: September 2025
    try:
        date = datetime.strptime(date_string, "%B %Y")
        return date.strftime("%Y-%m-%d"), "month"
    except ValueError:
        pass

    # Google News: Thu, 28 May 2026 07:00:00 GMT
    try:
        date = parsedate_to_datetime(date_string)
        return date.strftime("%Y-%m-%d"), "day"
    except (ValueError, TypeError):
        pass

    raise ValueError(f"Unrecognised date format: {date_string}")