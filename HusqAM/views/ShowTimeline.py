from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from HusqAM.models import Robot, Status


# mowerStatesList = (
#     "OK_LEAVING", "OK_CUTTING", "OK_CUTTING_NOT_AUTO", "OK_SEARCHING", "OK_CHARGING",
#     "PAUSED", "PARKED_TIMER", "PARKED_PARKED_SELECTED",
#     "OFF_HATCH_OPEN", "OFF_HATCH_CLOSED",
#     "??? UNKNOWN",
# )


class Day:
    def __init__(self):
        self.states = []


@login_required
def Daily(request, robot_id):
    robot = get_object_or_404(Robot, id=robot_id)
    all_states = robot.status_set.all()

    this_state = Status(
        robot=robot,
        timestamp=all_states[0].timestamp.replace(hour=0, minute=0, second=0, microsecond=0),
        mowerStatus="unknown"
    )

    days = []
    day = Day()
    day_left = 1440

    for next_state in all_states:
        duration_left = int((next_state.timestamp - this_state.timestamp).total_seconds()) // 60

        while duration_left:
            if duration_left <= day_left:
                day.states.append((duration_left, this_state))
                day_left -= duration_left

                duration_left = 0
            else:
                day.states.append((day_left, this_state))
                duration_left -= day_left

                days.append(day)
                day = Day()
                day_left = 1440

        # prepare the next iteration
        this_state = next_state

    # add a final span to complete the last day
    if day_left > 0:
        day.states.append((day_left, this_state))
        days.append(day)

    return render(request, 'HusqAM/ShowTimelineDaily.html', {
        'robot': robot,
        'days': days,
    })
