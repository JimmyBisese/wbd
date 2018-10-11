from django.core.management.base import BaseCommand
from wbddata.models import WBD
from django.conf import settings
import os
from datetime import datetime as dt
import csv

# this is slow, but it uses django to load, rather than doing it outside of the ORM
# (venv) C:\inetpub\wwwdjango\wbd>python manage.py load_huc12_attributes
#
#  Loaded 83018 rows in 1646.9344 seconds

#
def transform_traveltime_hr(traveltime_hrs):
    try:
        return float(traveltime_hrs)
    except:
        return None

def transform_area_sq_km(area_sq_km):
    try:
        return float(area_sq_km)
    except:
        return None

class Command(BaseCommand):
    args = '<none>'
    help = 'load data from CSV file settings.HUC12_ATTRIBUTES_FILE into ORM "WBD"'

    def _create_data(self):
        startTime = dt.now()
        path = settings.HUC12_ATTRIBUTES_FILE

        if not len(path):
            raise ValueError('settings.HUC12_ATTRIBUTES_FILE must be set before calling this function')
        if not os.path.exists(path):
            raise IOError("Unable to attributes file path\n\t%s" % (path))

        row_count = 0
        with open(path) as f:
            reader = csv.reader(f)
            next(reader, None)  # skip the headers
            for row in reader:
                row_count += 1

                huc_code = row[0]
                if len(huc_code) % 2 != 0:
                    huc_code = '0' + huc_code

                _, created = WBD.objects.get_or_create(

                    huc_code=row[0],
                    name=row[1],
                    area_sq_km=transform_area_sq_km(row[2]),
                    water_area_sq_km=row[3],
                    comid=row[4],
                    huc12_ds=row[5],
                    distance_km=row[6],
                    traveltime_hrs=transform_traveltime_hr(row[7]),
                    multiple_outlet_bool=row[8],
                    sink_bool=row[9],
                    headwater_bool=row[10],
                    terminal_bool=row[11],
                    terminal_huc12_ds=row[12],
                    terminal_outlet_type_code=row[13],
                    huc12_ds_count_nu=row[14],

                )

        print(" Loaded %s rows in %s seconds" % (row_count, (dt.now() - startTime).total_seconds()))


    def handle(self, *args, **options):
        self._create_data()