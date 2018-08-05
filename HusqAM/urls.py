from django.conf.urls import url
# from django.contrib.auth import views as auth_views
# from django.urls import reverse_lazy
from .views import home, LoadJSON, ShowTimeline


app_name = 'husqam'

urlpatterns = [
    url(r'^$', home.handle_request, name='home'),
    url(r'^load-json/$', LoadJSON.load_json, name='load-json'),
    url(r'^robot/(?P<robot_id>\d+)/daily/$', ShowTimeline.Daily, name='robot-daily'),
    url(r'^robot/shared/(?P<anon_id>[\w\d]+)/$', ShowTimeline.SharedDaily, name='robot-shared'),

    # url(r'^$', Startseite.StelleDar, name='startseite'),
    # url(r'^hilfe/$', Hilfe.StelleDar, name='hilfe'),
    # url(r'^anmelden/$', auth_views.LoginView.as_view(template_name='Lori/auth_anmelden.html'), name='anmelden'),
    # url(r'^abmelden/$', auth_views.LogoutView.as_view(template_name='Lori/auth_abgemeldet.html'), name='abmelden'),
    # url(r'^passwort-ändern/$', auth_views.PasswordChangeView.as_view(template_name='Lori/auth_Passwort_aendern.html', success_url=reverse_lazy('lori:passwort-geändert')), name='passwort-ändern'),
    # url(r'^passwort-geändert/$', auth_views.PasswordChangeDoneView.as_view(template_name='Lori/auth_Passwort_geaendert.html'), name='passwort-geändert'),
]
