import xml
import re

def strip_ns(d):
    if isinstance(d,dict):
        return {re.sub(r'\{.*\}','',k): strip_ns(v) for k, v in d.iteritems()}
    if isinstance(d, list):
        return [strip_ns(x) for x in d]
    return d