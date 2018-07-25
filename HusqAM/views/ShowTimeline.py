from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from HusqAM.models import Robot, Status


class Span:
    def __init__(self, minutes, state):
        self.minutes = minutes
        self.percent = minutes / 1440.0
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

            "OFF_HATCH_OPEN": "progress-bar-danger",
            "OFF_HATCH_CLOSED": "progress-bar-danger",

            "unknown": "progress-bar-striped",  # kommt immer am ersten Tag ganz am Anfang vor
            "ERROR": "progress-bar-danger progress-bar-striped",
        }.get(self.state.mowerStatus, "progress-bar-danger")


class Day:
    def __init__(self):
        self.spans = []


@login_required
def Daily(request, robot_id):
    robot = get_object_or_404(Robot, id=robot_id)
    all_states = robot.status_set.all()

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
    day = Day()
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
                day.spans.append(Span(duration_left, this_state))
                day_left -= duration_left

                duration_left = 0
            else:
                day.spans.append(Span(day_left, this_state))
                duration_left -= day_left

                days.append(day)
                day = Day()
                day_left = 1440

        # prepare the next iteration
        this_state = next_state

    # add a final span to complete the last day
    if day_left > 0:
        day.spans.append(Span(day_left, this_state))
        days.append(day)

    return render(request, 'HusqAM/ShowTimelineDaily.html', {
        'robot': robot,
        'days': days,
    })
