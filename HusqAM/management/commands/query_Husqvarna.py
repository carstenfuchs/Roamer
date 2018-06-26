from django.conf import settings
from django.core.management.base import BaseCommand
import pprint, pyhusmow
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Ruft den logischen Zustand und die aktuellen Betriebsdaten der Mäher von www.husquarna.com ab und aktualisiert damit (--update-database) die Datenbank."

    def add_arguments(self, parser):
        parser.add_argument('-u', '--update-database', action='store_true', help='Aktualisiere die Datenbank mit den abgerufenen Informationen.')

    def handle(self, *args, **options):
        # Das Token ist wie ein Cookie: Daran erkennt der Husquarna-Server uns wieder.
        mow = pyhusmow.API()
        tc = pyhusmow.TokenConfig()
        tc.load_config()

        if tc.token_valid():
            mow.set_token(tc.token, tc.provider)
        else:
            expire = mow.login(settings.HUSQVARNA_USERNAME, settings.HUSQVARNA_PASSWORD)
            tc.token = mow.token
            tc.provider = mow.provider
            tc.expire_on = datetime.now() + timedelta(0, expire)
            tc.save_config()
            self.stdout.write('Created a new token.')

        for robot in mow.list_robots():
            s = pprint.pformat(robot, indent=4)
            self.stdout.write(s)
            self.stdout.write("\n")

            # mow.select_robot(robot['id'])
            # s = pprint.pformat(mow.status(), indent=4)
            # self.stdout.write(s)
            # self.stdout.write("\n")
