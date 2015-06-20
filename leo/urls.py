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
    url(r'^vehicle_owner/$', 'leo_app.views.vehicle_owner'),
)

urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )

# pos_year_1 = SubjectReferral.objects.filter(hiv_result='POS',subject_visit__appointment__visit_definition__code='T0', subject_visit__household_member__household_structure__household__plot__community__in=['digawana', 'ranaka', 'molapowabojang', 'otse'])
# pos_year_1 = pos_year_1.order_by('subject_visit__household_member__household_structure__household__plot__community')
# new_pos_year_2=[]
# count = 0
# for ref in pos_year_1:
#     try:
#         subject_ref = SubjectReferral.objects.get(subject_identifier=ref.subject_identifier, new_pos=True, subject_visit__appointment__visit_definition__code='T1')
#         new_pos_year_2.append(subject_ref)
#     except:
#         pass
#     count = count + 1
#     print count
# 
# f = open('/home/django/incorrect_new_pos.txt','w')
# 
# for entry in new_pos_year_2:
#     f.write('{},{},{},{},{},\n'.format(entry.subject_identifier, entry.hiv_result, entry.referral_code, entry.new_pos, entry.subject_visit.household_member.household_structure.household.plot.community))