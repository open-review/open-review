# Django DiscoverRunner searches for test*.py files, which doesn't find modules. This
# hack works around this.
from openreview.apps.main.tests import *
