from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:

    url(r'^$', 'chitter_app.views.index'),
    url(r'^login$', 'chitter_app.views.login_view'),
    url(r'^logout$', 'chitter_app.views.logout_view'),
    url(r'^signup$', 'chitter_app.views.signup'),
    url(r'^chitters$', 'chitter_app.views.public'),
    url(r'^submit$', 'chitter_app.views.submit'),
    url(r'^users/$', 'chitter_app.views.users'),
    url(r'^users/(?P<username>\w{0,30})/$', 'chitter_app.views.users'),
    url(r'^follow$', 'chitter_app.views.follow'),


)
