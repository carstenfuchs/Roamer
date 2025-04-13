#from datetime import datetime
import requests
import urllib3

from django.conf import settings
from django.core.management.base import BaseCommand


urllib3.disable_warnings()


class Command(BaseCommand):
    help = "Queries the Husqvarna Automower Connect API."

    # def add_arguments(self, parser):
    #     parser.add_argument('username', help='The user whose Husqvarna account should be queried.')
    #     parser.add_argument('-u', '--update-database', action='store_true', help='Aktualisiert die lokale Datenbank mit den abgerufenen Informationen.')
    #     parser.add_argument('-p', '--post-to-remote', metavar='URL', help='Sendet die abgerufenen Informationen per POST Request an den entfernten Server.')
    #     parser.add_argument('-l', '--local-shortcut', action='store_true', help='Skips -p and -u if a local file cache indicates that the data has not changed.')

    def handle(self, *args, **options):
        try:
            r = requests.post(
                "https://api.authentication.husqvarnagroup.dev/v1/oauth2/token",
                data={
                    # Obtain the access token per password grant:
                    # https://developer.husqvarnagroup.cloud/docs/api
                    'grant_type': 'password',
                    # The `client_id` must be the application key from:
                    # https://developer.husqvarnagroup.cloud/apps > Roamer > Application Key
                    'client_id': 'a9524c6a-291d-4b4c-98c6-9f65b2e0c9de',
                    'username': 'info@cafu.de',
                    'password': 'Rhzyvoo1',
                },
                timeout=8.0,
                verify=False,
            )

            # r = requests.post(
            #     "https://api.amc.husqvarna.dev/v1",
            #     data={
            #         # https://developer.husqvarnagroup.cloud/apps > Roamer > Application Key
            #         'X-Api-Key': 'a9524c6a-291d-4b4c-98c6-9f65b2e0c9de',
            #         'Authorization-Provider': 'husqvarna',
            #         'Authorization': 'Bearer test_accessToken',
            #     },
            #     timeout=8.0,
            #     verify=False,
            # )
        except requests.exceptions.Timeout as e:
            print(str(e))
            return

        if r.status_code != 200:
            print(f"{r.status_code = } != 200")
            return

        try:
            json = r.json()
        except requests.exceptions.JSONDecodeError as e:
            print(str(e))
            return

        print("OK")
        print(json)
