
from re import sub as re_sub


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re_sub(r'[^-\w.]', "", s)
