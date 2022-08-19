import string
import random
import math

def random_value_generator(size=10, chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        size, srepr = bytes / 1099511627776, "TB"
    elif bytes >= 1073741824:
        size, srepr = bytes / 1073741824, "GB"
    elif bytes >= 1048576:
        size, srepr = bytes / 1048576, "MB"
    elif bytes >= 1024:
        size, srepr = bytes / 1024, "KB"
    else:
        size, srepr = bytes, " bytes"
    return "%d%s" % (math.ceil(size), srepr)