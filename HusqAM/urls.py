from django.urls import path
from HusqAM.views import home, LoadJSON, ShowTimeline


app_name = 'husqam'

urlpatterns = [
    path('', home.handle_request, name='home'),
    path('load-json/', LoadJSON.load_json, name='load-json'),
    path('robot/<int:robot_id>/daily/', ShowTimeline.Daily, name='robot-daily'),
    path('robot/shared/<str:anon_id>/', ShowTimeline.SharedDaily, name='robot-shared'),

    # url(r'^$', Startseite.StelleDar, name='startseite'),
    # url(r'^hilfe/$', Hilfe.StelleDar, name='hilfe'),
    # url(r'^anmelden/$', auth_views.LoginView.as_view(template_name='Lori/auth_anmelden.html'), name='anmelden'),
    # url(r'^abmelden/$', auth_views.LogoutView.as_view(template_name='Lori/auth_abgemeldet.html'), name='abmelden'),
    # url(r'^passwort-ändern/$', auth_views.PasswordChangeView.as_view(template_name='Lori/auth_Passwort_aendern.html', success_url=reverse_lazy('lori:passwort-geändert')), name='passwort-ändern'),
    # url(r'^passwort-geändert/$', auth_views.PasswordChangeDoneView.as_view(template_name='Lori/auth_Passwort_geaendert.html'), name='passwort-geändert'),
]
