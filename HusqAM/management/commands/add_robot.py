from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from HusqAM.models import Robot


class Command(BaseCommand):
    help = "Legt für den angegebenen User in der lokalen Datenbank einen weiteren Roboter an."

    def add_arguments(self, parser):
        parser.add_argument('-u', '--user', required=True, help='Der Name des Benutzers, für den der Roboter angelegt werden soll.')
        parser.add_argument('-i', '--id', required=True, help='Die Hersteller-ID des Roboters (kann mit `query_Husqvarna` abgerufen werden).')

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options['user'])
        except User.DoesNotExist:
            self.stderr.write('A user with username "{}" does not exist.'.format(options['user']))
            return

        try:
            r = Robot.objects.get(manufac_id=options['id'])
            self.stderr.write('A robot with this ID already exists: "{}", owned by {}.'.format(r, user))
            return
        except Robot.DoesNotExist:
            pass

        Robot.objects.create(owner=user, manufac_id=options['id'])

        self.stdout.write('All robots for {}:'.format(user))
        for r in Robot.objects.filter(owner=user):
            self.stdout.write(str(r))
