import os
import shlex
import string
import shutil
import random
import asyncio
import subprocess
from typing import Union


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


def get_readable_bytes(size: Union[int, str]) -> str:
    """
    Return a human readable file size from bytes.
    """

    UNIT_SUFFIXES = ["B", "KiB", "MiB", "GiB", "TiB"]

    if isinstance(size, str):
        size = int(size)

    if size < 0:
        raise ValueError("Size must be positive")
    if size == 0:
        return "0 B"

    i = 0
    while size >= 1024 and i < len(UNIT_SUFFIXES) - 1:
        size /= 1024
        i += 1

    return f"{size:.2f} {UNIT_SUFFIXES[i]}"


def get_readable_bitrate(bitrate_kbps):
    """
    Return a human-readable bitrate size.
    """

    if bitrate_kbps > 10000:
        bitrate = str(round(bitrate_kbps / 1000, 2)) + " " + "Mb/s"
    else:
        bitrate = str(round(bitrate_kbps, 2)) + " " + "kb/s"

    return bitrate


def remove_N(seq):
    """
    Remove consecutive duplicates from the input sequence.
    """

    i = 1
    while i < len(seq):
        if seq[i] == seq[i - 1]:
            seq.pop(i)
            i -= 1
        i += 1


def makedir(name: str):
    """
    Create a directory with the specified name.
    If a directory with the same name already exists, it will be removed and a new one will be created.
    """

    if os.path.exists(name):
        shutil.rmtree(name)
    os.mkdir(name)


def check_and_convert_time(time: str):
    """
    Return the time in seconds if the time format is correct (i.e, HH:MM:SS).
    Return False otherwise.
    """

    try:
        time = str(time)
        hours, minutes, seconds = map(int, time.split(":"))
        if 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59:
            return int(3600 * hours + 60 * minutes + seconds)
        else:
            return False
    except ValueError:
        return False


def randstr(length=7):
    """
    Generate a random string of lowercase letters and digits with the specified length.
    The default length is 7.
    """

    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


async def async_subprocess(command: str) -> str:
    """
    Asynchronously run a shell command and return its output as a string.

    Args:
        command (str): The command to run in the shell.

    Returns:
        str: The output of the shell command, including stdout and stderr.

    """

    args = shlex.split(command)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    return str(stdout.decode().strip()) + str(stderr.decode().strip())
