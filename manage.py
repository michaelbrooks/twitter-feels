#!/usr/bin/env python
import os
import sys

def read_env(envFile='.env'):
    try:
        with open(envFile) as f:
            content = f.read()
    except IOError:
        content = ''

    import re
    values = {}
    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)

            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)

            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))

            values[key] = val
    os.environ.update(values)

if __name__ == "__main__":

    read_env()
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "twitter_feels.settings.dev")

    from django.core.management import execute_from_command_line


    execute_from_command_line(sys.argv)
