from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'regis.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^signup/$', 'regis.views.signup'),
    url(r'^confirm_email', 'regis.views.user_email_confirm', name='signup_confirm_email'),
    url(r'^accounts/login/$', 'regis.views.user_login', name='login'),
    url(r'^accounts/logout/$', 'regis.views.logout', name='logout'),
    (r'^accounts/loggedin/$', 'regis.views.loggedin'),
    (r'^password_reset/$', 'regis.views.password_reset'),
    url(r'^password_reset_mail','regis.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'', include('social_auth.urls')),
)
