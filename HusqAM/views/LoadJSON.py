import json
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from HusqAM.models import Robot
from HusqAM.utils import process_pyhusmow_dict


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
            self.add_error("json", de)
            return cd

        if isinstance(cd['robot_dicts'], dict):
            cd['robot_dicts'] = [cd['robot_dicts']]

        if not isinstance(cd['robot_dicts'], list):
            self.add_error("json", "Input must be an object or array of objects.")
            return cd

        return cd


@csrf_exempt
def load_json(request):
    if request.method != 'POST':
        # It's a GET request – not our intended use case, except for debugging.
        form = LoadJsonForm()
        return render(request, 'HusqAM/LoadJSON.html', {'form': form})

    # It's a POST request, create a form with "bound" data.
    form = LoadJsonForm(request.POST)

    if not form.is_valid():
        # There were errors in the form data.
        return HttpResponse(
            "There were errors in the form data:\n" + json.dumps(form.errors, indent=4),
            content_type="text/plain; charset=utf-8"
        )

    # It's a POST request and the form data is valid.
    cd =  form.cleaned_data
    result = []

    for robot_dict in cd['robot_dicts']:
        if not robot_dict.get('id'):
            # Silently ignore this problem.
            continue

        robot, created = Robot.objects.get_or_create(owner=cd['user'], manufac_id=robot_dict['id'])
        robot_changes, new_state = process_pyhusmow_dict(robot, robot_dict)

        result.append("{} – robot changes: {}{}".format(robot, "created new instance, " if created else "", ", ".join(robot_changes) or "none"))
        result.append("{} – state changed: {}".format(robot, new_state.mowerStatus if new_state else "no"))

    if not result:
        result.append("The input did not contain any data.")

    # Normally we would redirect after a POST request, so that the request isn't repeated
    # when the user hits "Refresh" in the browser. However, this view is not intended to
    # be loaded in a browser, so we send a straight reply with the result instead.
    return HttpResponse("\n".join(result), content_type="text/plain; charset=utf-8")
