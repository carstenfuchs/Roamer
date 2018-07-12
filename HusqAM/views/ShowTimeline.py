import json
from calendar import timegm
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from HusqAM.models import Robot, Status


@login_required
def Daily(request, robot_id):
    robot = get_object_or_404(Robot, id=robot_id)
    series = {}
    problems = []

    mowerStatesList = (
        "OK_LEAVING", "OK_CUTTING", "OK_CUTTING_NOT_AUTO", "OK_SEARCHING", "OK_CHARGING",
        "PAUSED", "PARKED_TIMER", "PARKED_PARKED_SELECTED",
        "OFF_HATCH_OPEN", "OFF_HATCH_CLOSED",
        "??? UNKNOWN",
    )

    for mowerStatus in mowerStatesList:
        series[mowerStatus] = {
            'name': mowerStatus,
          # 'color': '',
            'data': [],
        }

    for st in robot.status_set.all():
        # Highcharts nimmt per Voreinstellungen Daten und Zeiten in UTC entgegen, als Millisekunden seit der Unix-Epoche.

        # Beachte, dass calendar.timegm() die Inverse von time.gmtime() (nicht von time.mktime()) ist:
        # http://docs.python.org/library/calendar.html#calendar.timegm
        # ts = st.timestamp
        # day = datetime(ts.year, ts.month, ts.day)   # time component is 0:00:00
        # x = timegm( day.utctimetuple() ) * 1000.0
        # y = (ts.hour * 3600 + ts.minute * 60) * 1000.0

        x = st.timestamp.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000.0
        y = st.timestamp.replace(year=1970, month=1, day=1).timestamp() * 1000.0

        if st.mowerStatus not in series:
            problems.append("Unknown mower state „{}“ encountered.".format(st.mowerStatus))
            st.mowerStatus = "??? UNKNOWN"

        series[st.mowerStatus]['data'].append({
            'name': st.mowerStatus,
            'x': x,
            'y': y,
        })

    return render(request, 'HusqAM/ShowTimelineDaily.html', {
        'robot': robot,
        'series': json.dumps(list(series.values())),
        'problems': problems,
    })
