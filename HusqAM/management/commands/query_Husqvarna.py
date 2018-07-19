from datetime import datetime, timedelta
import json, pyhusmow, requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from HusqAM.models import Robot, Status
from HusqAM.utils import process_pyhusmow_dict


class Command(BaseCommand):
    help = "Ruft den logischen Zustand und die aktuellen Betriebsdaten der Mäher von husqvarnagroup.net ab."

    def add_arguments(self, parser):
        parser.add_argument('username', help='The user whose Husqvarna account should be queried.')
        parser.add_argument('-u', '--update-database', action='store_true', help='Aktualisiert die lokale Datenbank mit den abgerufenen Informationen.')
        parser.add_argument('-p', '--post-to-remote', metavar='URL', help='Sendet die abgerufenen Informationen per POST Request an den entfernten Server.')

    def get_list_robots(self, user, mowAPI):
        for connection_attempt in (1, 2, 3):
            try:
                if user.husaccount.update_connection(mowAPI, force_new_token=(connection_attempt > 1)):
                    self.stdout.write('Created a new token.')

                return mowAPI.list_robots()

            except requests.exceptions.HTTPError as e:
                # Most likely the token in user.husaccount expired earlier than expected.
                self.stderr.write('There was a connection problem:\n{}\nTrying again...'.format(e))

    def handle(self, *args, **options):
        # Das Token ist wie ein Cookie: Daran erkennt der Husqvarna-Server uns wieder.
        user = User.objects.get(username=options['username'])
        mow = pyhusmow.API()
        list_robots = self.get_list_robots(user, mow)

        if not list_robots:
            raise CommandError('Cannot get the list of robots. Quit.')

        if options['verbosity'] > 0:    # local console output
            for robot_dict in list_robots:
                self.stdout.write(json.dumps(robot_dict, indent=4))
                self.stdout.write("\n")

                # mow.select_robot(robot['id'])
                # s = pprint.pformat(mow.status(), indent=4)
                # self.stdout.write(s)
                # self.stdout.write("\n")

        if options['update_database']:
            for robot_dict in list_robots:
                try:
                    robot = Robot.objects.get(manufac_id=robot_dict['id'])
                except Robot.DoesNotExist:
                    self.stderr.write('The robot with ID "{}" does not exist.\nUse the `add_robot` command to add it.'.format(robot_dict['id']))
                    continue

                robot_changes, new_state = process_pyhusmow_dict(robot, robot_dict)

                self.stdout.write("{} – robot changes: {}".format(robot, ", ".join(robot_changes) or "none"))
                self.stdout.write("{} – state changed: {}".format(robot, new_state.mowerStatus if new_state else "no"))

        if options['post_to_remote']:
            payload = {
                'username': settings.QUERY_HUSQVARNA_POST_REMOTE_SERVER_USERNAME,
                'password': settings.QUERY_HUSQVARNA_POST_REMOTE_SERVER_PASSWORD,
                'json': json.dumps(list_robots, indent=4),
            }

            r = requests.post(options['post_to_remote'], data=payload)
            self.stdout.write("Server response at {}:".format(timezone.now()))
            self.stdout.write(r.text)
