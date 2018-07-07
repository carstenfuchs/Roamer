import json
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from HusqAM.models import Robot


class LoadJsonForm(forms.Form):
    username = forms.CharField(max_length=40, help_text="The user whose mowers the posted information relates to.")
    password = forms.CharField(max_length=40, widget=forms.PasswordInput, help_text="The user's login password.")
    json = forms.CharField(max_length=10000, widget=forms.Textarea, help_text="The state of one or more mowers, in JSON format as output by the `query_Husqvarna` command.")

    def clean(self):
        cd = self.cleaned_data

        if self.errors:
            return cd

        cd['user'] = authenticate(username=cd['username'], password=cd['password'])

        if cd['user'] is None:
            raise forms.ValidationError("Please provide a valid username and password.")

        try:
            cd['robot_dicts'] = json.loads(cd['json'])
        except json.JSONDecodeError as de:
            raise forms.ValidationError(de)

        if isinstance(cd['robot_dicts'], dict):
            cd['robot_dicts'] = [cd['robot_dicts']]

        if not isinstance(cd['robot_dicts'], list):
            self.add_error("json", "Input must be an object or array of objects.")

        return cd


# @login_required
def load_json(request):
    if request.method == 'POST':
        # Es wurden Formular-Daten übermittelt - erzeuge eine Form die an die POST Daten "gebunden" (bound) ist.
        form = LoadJsonForm(request.POST)

        if form.is_valid():
            cd =  form.cleaned_data
            num_robots = 0

            for robot_dict in cd['robot_dicts']:
                try:
                    robot = Robot.objects.get(owner=cd['user'], manufac_id=robot_dict.get('id'))
                except Robot.DoesNotExist:
                    continue

                changes = robot.update_from_dict(robot_dict)
                num_robots += 1

                if changes:
                    robot.save()
                    messages.success(request, "{} has been updated ({}).".format(robot, ", ".join(changes)))
                else:
                    messages.info(request, "There were no changes for {}.".format(robot))

            if num_robots == 0:
                messages.warning(request, "The input did not contain data for any of {}'s robots.".format(cd['user']))

            # Redirect after POST, so that the request isn't repeated when the user hits "Refresh".
            return HttpResponseRedirect(reverse("husqam:load-json"))

    else:
        # Es wurden keine Formular-Daten übermittelt - lege eine neue "unbound" Form mit Initialwerten an.
        form = LoadJsonForm()

    # Fertig! Ergebnisse an Template zum Rendern übergeben.
    return render(request, 'HusqAM/LoadJSON.html', {'form': form})
