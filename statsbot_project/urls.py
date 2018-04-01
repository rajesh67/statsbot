"""statsbot_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from app.views import home
from shopping.views import AboutUSView, WhyUSView
from django.conf.urls import handler404, handler500

handler404 = 'shopping.views.handler404'
handler500 = 'shopping.views.handler500'

urlpatterns = [
    url('^admin/', admin.site.urls),
    url('^$', home ,name="home"),
    url('^about-us/$', AboutUSView.as_view(),name="about-us"),
    url('^why-us/$', WhyUSView.as_view(),name="why-us"),
    # Online Shopping App
    url(r'^shopping/', include('shopping.urls')),
    # Online trael App
    url(r'^flights/', include('flights.urls')),
    # Online Bus Bookings
    url(r'^buses/', include('busses.urls')),
    # Online Hotel Bookings
    url(r'^hotels/', include('hotels.urls')),
]

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
	urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)