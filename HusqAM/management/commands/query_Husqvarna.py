from datetime import datetime, timedelta
import json, pyhusmow
from django.conf import settings
from django.core.management.base import BaseCommand
from HusqAM.models import Robot


class Command(BaseCommand):
    help = "Ruft den logischen Zustand und die aktuellen Betriebsdaten der Mäher von www.husquarna.com ab."

    def add_arguments(self, parser):
        parser.add_argument('-u', '--update-database', action='store_true', help='Aktualisiert die lokale Datenbank mit den abgerufenen Informationen.')
        parser.add_argument('-p', '--post-to-remote', metavar='SERVER', help='Sendet die abgerufenen Informationen per POST Request an den entfernten Server.')

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

        for robot_dict in mow.list_robots():
            self.stdout.write(json.dumps(robot_dict, indent=4))
            self.stdout.write("\n")

            # mow.select_robot(robot['id'])
            # s = pprint.pformat(mow.status(), indent=4)
            # self.stdout.write(s)
            # self.stdout.write("\n")

        if options['update_database']:
            for robot_dict in mow.list_robots():
                robot = Robot.objects.get(manufac_id=robot_dict['id'])
                changes = robot.update_from_dict(robot_dict)
                robot.save()
                self.stdout.write(str(robot) + " – ", ending="")
                self.stdout.write(", ".join(changes) if changes else "keine Änderungen")

        if options['post_to_remote']:
            pass
