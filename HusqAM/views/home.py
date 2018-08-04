#from datetime import date, timedelta

#from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render

#from Lori.libs.common import getDateToday
#from Lori.models import Erfasst, UserProfile


#@login_required
@transaction.non_atomic_requests
def handle_request(request):

    return render(request, "HusqAM/home.html", {
        "public_robots": None,
    })
