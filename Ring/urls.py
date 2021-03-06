from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/?$','api.views.index'),
    url(r'^group_signup?$','api.views.group_signup'),
    url(r'^dashboard/?$','api.views.dashboard'),
    url(r'^sign_in/?$','api.views.sign_in'),
    url(r'^create_user/?$','api.views.create_user'),
    url(r'^dashboard/create_group/?$','api.views.create_group'),
    url(r'^dashboard/group?$','api.views.group'),
    url(r'^members/?$','api.views.group_members'),
    url(r'^bulletin/?$','api.views.group_bulletin'),
    url(r'^bulletin/pin_new_item?$','api.views.pin_new_item'),
    url(r'^members/add_user_to_group?$','api.views.add_user_to_group'),
    url(r'^messages/?$','api.views.group_messages'),
    url(r'^messages/send_new_message?$','api.views.send_new_message'),
    url(r'', include('social_auth.urls')),
    url(r'^authenticated/$', 'api.views.show_docs'),
    # Examples:
    # url(r'^$', 'Ring.views.home', name='home'),
    # url(r'^Ring/', include('Ring.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
