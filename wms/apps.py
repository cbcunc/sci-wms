# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

import pytz
from datetime import datetime, timedelta
from wms import logger


class WmsConfig(AppConfig):
    name = 'wms'
    verbose_name = "WMS"

    def ready(self):
        # Initialize signals
        import wms.signals
