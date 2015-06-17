from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'leo_app.views.index'), # root
    url(r'^login$', 'leo_app.views.login_view'), # login
    url(r'^logout$', 'leo_app.views.logout_view'), # logout
    url(r'^signup$', 'leo_app.views.signup'), # signup
    url(r'^ribbits$', 'leo_app.views.public'), # public ribbits
    url(r'^submit$', 'leo_app.views.submit'), # submit new ribbit
    url(r'^users/$', 'leo_app.views.users'),
    url(r'^users/(?P<username>\w{0,30})/$', 'leo_app.views.users'),
    url(r'^user_profile/(?P<username>\w{0,30})/$', 'leo_app.views.user_profile'),
    url(r'^user_profile/$', 'leo_app.views.user_profile'),
    url(r'^follow$', 'leo_app.views.follow'),
)

urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )