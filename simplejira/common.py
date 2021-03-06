import re
from datetime import datetime

import editor
import pkg_resources
import iso8601
from dateutil import tz, parser


class PkgResource(object):
    ASCII_ART = 'ascii_art.txt'
    DEFAULT_CONFIG = 'config_default.yml'
    ISSUE_TEMPLATE = 'issue_template.yml'

    @staticmethod
    def get_path(path):
        return pkg_resources.resource_filename(__name__, 'resources/' + path)

    @staticmethod
    def read(path):
        with open(PkgResource.get_path(path)) as f:
            return f.read()

def editor_ignore_comments(default_text):
    """
    Open pyeditor but ignore lines starting with "#" when text is returned.

    :param default_text:
    :return:
    """
    edited_text = editor.edit(contents=default_text)
    lines = edited_text.split('\n')
    return "\n".join([line for line in lines if not line.startswith("#")])


def sanitize_worklog_time(s):
    """
    Convert a time string entered by user to jira-acceptable format for issue time tracking
    """
    s = s.replace(' ', '')

    def get_number_before(letter):
        number = 0
        try:
            regex_str = r'\D*(\d*)\s*{}.*'.format(letter)
            number = re.findall(regex_str, s)[0]
        except (AttributeError, IndexError):
            pass
        return number

    days = get_number_before('d')
    hours = get_number_before('h')
    mins = get_number_before('m')
    secs = get_number_before('s')

    new_s = ""
    new_s += days + "d " if days else ""
    new_s += hours + "h " if hours else ""
    new_s += mins + "m " if mins else ""
    new_s += secs + "s " if secs else ""
    if new_s:
        return new_s
    else:
        # user might not have specified any strings at all, just pass along the int
        return s


def friendly_worklog_time(seconds):
    """
    https://stackoverflow.com/questions/775049/how-to-convert-seconds-to-hours-minutes-and-seconds

    :param seconds:
    :return:
    """
    if not seconds:
        string = "0m"
    else:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        string = ""
        string += "{}h".format(h) if h else ""
        string += "{}m".format(m) if m else ""
        string += "{}s".format(s) if s else ""
    return string


def iso_to_datetime(string):
    tz_utc = tz.tzutc()
    tz_local = tz.tzlocal()
    utc_datetime = iso8601.parse_date(string)
    utc_datetime = utc_datetime.replace(tzinfo=tz_utc)
    return utc_datetime.astimezone(tz_local)


# For now, instead of using hard-coded datetime formats
# we'll use %c for datetime->string and for string->datetime
# just use dateutil's parser

#TIME_FORMAT = '%a %d %b %Y %I:%M:%S %p %Z'


def iso_to_ctime_str(string):
    datetime_object = iso_to_datetime(string)
    return datetime_object.strftime('%c')


def ctime_str_to_datetime(datetime_string):
    return parser.parse(datetime_string)


def ctime_str_to_iso(datetime_string):
    return ctime_str_to_datetime(datetime_string).isoformat()


def iso_time_is_today(string):
    datetime_object = iso_to_datetime(string)
    return datetime.today().date() == datetime_object.date()
