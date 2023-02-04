import os
import string
import shutil
import random


def get_readable_time(seconds: int) -> str:
    """
    Return a human-readable time format
    """

    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)

    if days != 0:
        result += f"{days}d "
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)

    if hours != 0:
        result += f"{hours}h "
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)

    if minutes != 0:
        result += f"{minutes}m "

    seconds = int(seconds)
    result += f"{seconds}s "
    return result

def get_readable_bytes(size: str) -> str:
    """
    Return a human readable file size from bytes.
    """

    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}

    if not size:
        return ""
    power = 2**10
    raised_to_pow = 0

    while size > power:
        size /= power
        raised_to_pow += 1

    return f"{str(round(size, 2))} 

def get_readable_bytes(value, digits=2, delim="", postfix=""):
    """
    Return a human-readable file size.
    """

    if value is None:
        return None
    chosen_unit = "B"
    for unit in ("KiB", "MiB", "GiB", "TiB"):
        if value > 1000:
            value /= 1024
            chosen_unit = unit
        else:
            break
    return f"{value:.{digits}f}" + delim + chosen_unit + postfix


def get_readable_bitrate(bitrate_kbps):
    """
    Return a human-readable bitrate size.
    """
    
    if bitrate_kbps > 10000:
        bitrate = str(round(bitrate_kbps / 1000, 2)) + ' ' + 'Mb/s'
    else:
        bitrate = str(round(bitrate_kbps, 2)) + ' ' + 'kb/s'

    return bitrate


def makedir(name: str):
    if os.path.exists(name):
        shutil.rmtree(name)
    os.mkdir(name)


def remove_N(seq):
    i = 1
    while i < len(seq):
        if seq[i] == seq[i - 1]:
            del seq[i]
            i -= 1
        else:
            i += 1


def randstr():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
