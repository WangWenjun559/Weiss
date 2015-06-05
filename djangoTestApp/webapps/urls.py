from django.conf.urls import patterns, include, url
from django.contrib import admin
from testapp import views


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webapps.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.homepage, name='home'),
    url(r'^number$', views.showNumber),

)
