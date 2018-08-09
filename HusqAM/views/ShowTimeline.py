from datetime import timedelta
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from HusqAM.models import Robot, Status


ZeitraumAuswahl = [
    (1, "heute"),
    (7, "eine Woche"),
    (14, "zwei Wochen"),
    (28, "vier Wochen"),
    (90, "drei Monate"),
    (365, "ein Jahr"),
]


class EinstellungenForm(forms.Form):
    Zeitraum = forms.ChoiceField(choices=ZeitraumAuswahl,
                                 widget=forms.Select(attrs={"size": "1", "onchange": "submit()", "class": "form-control input-sm"}))

    Reihenfolge = forms.ChoiceField(choices=[("1", "heute zuerst"), ("2", "heute zuletzt")],
                                    widget=forms.Select(attrs={"size": "1", "onchange": "submit()", "class": "form-control input-sm"}))


class Span:
    def __init__(self, minutes, state):
        self.minutes = minutes
        self.percent = minutes / 1440.0 * 100.0
        self.state = state

    def get_css_class(self):
        return {
            "OK_LEAVING": "progress-bar-info",
            "OK_CUTTING": "progress-bar-success",
            "OK_CUTTING_NOT_AUTO": "progress-bar-success progress-bar-striped",
            "OK_SEARCHING": "progress-bar-info",

            "OK_CHARGING": "progress-bar-warning progress-bar-striped",

            # Keine CSS Klasse ergibt die Bootstrap-Default-Farbe, dunkelblau.
            "PAUSED": "progress-bar-striped",
            "PARKED_TIMER": "",     # kommt am häufigsten vor
            "PARKED_PARKED_SELECTED": "progress-bar-striped",
            "PARKED_DAILY_LIMIT": "progress-bar-striped",

            "OFF_HATCH_OPEN": "progress-bar-danger",
            "OFF_HATCH_CLOSED": "progress-bar-danger",

            "unknown": "progress-bar-striped",  # kommt immer am ersten Tag ganz am Anfang vor
            "ERROR": "progress-bar-danger progress-bar-striped",
        }.get(self.state.mowerStatus, "progress-bar-danger")


class Day:
    def __init__(self, date_):
        self.date_ = date_
        self.spans = []


def show_daily(request, robot):
    einst_form = EinstellungenForm(request.GET)

    if not einst_form.is_valid():
        einst_form = EinstellungenForm({'Zeitraum': 14, 'Reihenfolge': 1})
        assert einst_form.is_valid()

    now = timezone.now()
    all_states = list(robot.status_set.filter(timestamp__gt=now - timedelta(days=int(einst_form.cleaned_data['Zeitraum']))))

    all_states.append(Status(
        robot=robot,
        timestamp=now,
        mowerStatus="unknown"
    ))

    prev_tz = all_states[0].timestamp.tzinfo
    this_ts = all_states[0].timestamp.astimezone(timezone.get_current_timezone())
    this_ts = this_ts.replace(hour=0, minute=0, second=0, microsecond=0)
    this_ts = this_ts.astimezone(prev_tz)   # local midnight, expressed in prev_tz (UTC).

    this_state = Status(
        robot=robot,
        timestamp=this_ts,
        mowerStatus="unknown"
    )

    days = []
    day = Day(all_states[0].timestamp.astimezone(timezone.get_current_timezone()).date())
    day_left = 1440

    for next_state in all_states:
        # Naively, we would write:
        #   duration_left = int((next_state.timestamp - this_state.timestamp).total_seconds()) // 60
        # However, this loses time, as both the conversion to `int` and the
        # integer division cut off the fractional parts. To fix this, the lossy
        # computations must be done *before* the difference is computed.
        # (this_ts is an arbitrarily chosen reference. Any other value serves as well.)
        duration_left = int((next_state.timestamp - this_ts).total_seconds()) // 60 - \
                        int((this_state.timestamp - this_ts).total_seconds()) // 60

        while duration_left:
            if duration_left <= day_left:
                # The state ends still in this day.
                day.spans.append(Span(duration_left, this_state))
                day_left -= duration_left

                duration_left = 0
            else:
                # The state extends overnight, ending tomorrow.
                day.spans.append(Span(day_left, this_state))
                days.append(day)

                duration_left -= day_left
                day = Day(day.date_ + timedelta(days=1))
                day_left = 1440

        # prepare the next iteration
        this_state = next_state

    # if day_left > 0:
    #     # add a final span to complete the last day
    #     day.spans.append(Span(day_left, this_state))

    assert day.spans
    days.append(day)

    return render(request, 'HusqAM/ShowTimelineDaily.html', {
        'einst_form': einst_form,
        'robot': robot,
        'days': days if einst_form.cleaned_data['Reihenfolge'] == "2" else reversed(days),
    })


@login_required
def Daily(request, robot_id):
    robot = get_object_or_404(Robot, id=robot_id)

    if not request.user.is_superuser and robot.owner != request.user:
        # Should we rather raise Robot.DoesNotExist, that is, not reveal that the robot exists at all?
        raise PermissionDenied("You are not registered as the owner of this robot.")

    return show_daily(request, robot)


def SharedDaily(request, anon_id):
    robot = get_object_or_404(Robot, anon_id=anon_id)
    return show_daily(request, robot)
