#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openreview.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

    # Close selenium browser if needed
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        from openreview.apps.tools import testing
        if not testing.skip() and testing.same_browser():
            testing.WEBDRIVER.quit()
