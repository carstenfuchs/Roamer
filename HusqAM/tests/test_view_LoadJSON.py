from django.contrib.auth.models import User
from django.test import TestCase
from HusqAM.models import Robot


class UpdateDatabase_Test(TestCase):

    def test_empty_input(self):
        User.objects.create_user('carsten', 'some@email.com', 'secret')

        response = self.client.post("/load-json/", {
            'username': 'carsten',
            'password': 'secret',
            'json': '{}',
        }, follow=True)

        # print(response.content)
        self.assertRedirects(response, "/load-json/")
        self.assertContains(response, "alert-warning")
        self.assertContains(response, "The input did not contain data for any of carsten&#39;s robots.")

    def test_one_robot_no_changes(self):
        u = User.objects.create_user('carsten', 'some@email.com', 'secret')
        r = Robot.objects.create(owner=u, manufac_id='number 1')

        response = self.client.post("/load-json/", {
            'username': 'carsten',
            'password': 'secret',
            'json': """
                {
                    "id": "number 1",
                    "dummy": "not used"
                }
                """,
        }, follow=True)

        # print(response.content)
        self.assertRedirects(response, "/load-json/")
        self.assertContains(response, "alert-info")
        self.assertContains(response, "There were no changes for {}.".format(r))

    def test_update_two_robots(self):
        u = User.objects.create_user('carsten', 'some@email.com', 'secret')
        r1 = Robot.objects.create(owner=u, manufac_id='number 1')
        r2 = Robot.objects.create(owner=u, manufac_id='number 2')

        response = self.client.post("/load-json/", {
            'username': 'carsten',
            'password': 'secret',
            'json': """
                [
                {
                    "id": "number 1",
                    "model": "A",
                    "name": "Battlehorse",
                    "dummy": "not used"
                },
                {
                    "id": "number 2",
                    "model": "B",
                    "name": "Battleship",
                    "dummy": "not used"
                }
                ]
                """,
        }, follow=True)

        # print(response.content)
        self.assertRedirects(response, "/load-json/")
        self.assertContains(response, "alert-success", 2)
        self.assertContains(response, "{} has been updated (manufac_model, given_name).".format(Robot.objects.get(id=r1.id)))
        self.assertContains(response, "{} has been updated (manufac_model, given_name).".format(Robot.objects.get(id=r2.id)))
