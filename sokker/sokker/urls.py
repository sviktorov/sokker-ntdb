"""
URL configuration for sokker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.views.generic import TemplateView
import ntdb.urls
import tools.urls
import euro.urls

urlpatterns = [
    path("grappelli/", include("grappelli.urls")),  # grappelli URLS
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    # Define your app's URLs here
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("ntdb/", include(ntdb.urls)),
    path("tools/", include(tools.urls)),
    path("euro/", include(euro.urls)),
)


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
