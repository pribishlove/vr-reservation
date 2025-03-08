from datetime import datetime
import pytz


def convert_time(cur_time: str | datetime) -> datetime:
    if isinstance(cur_time, str):
        time_utc = datetime.fromisoformat(cur_time.rstrip("Z"))
    else:
        time_utc = cur_time

    local_timezone = pytz.timezone("Asia/Yekaterinburg")

    time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(local_timezone)

    return time_local.replace(tzinfo=None).replace(microsecond=0)
