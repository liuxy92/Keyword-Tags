"""tutorial URL Configuration

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
from django.urls import path, include
from django.conf.urls import url, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('snippets.urls'))
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]

# REST框架支持显式定义的模式视图或自动生成的模式。由于我们使用的是视图集和路由器，因此我们可以简单地使用自动模式生成。
from rest_framework.schemas import get_schema_view
#
# schema_view = get_schema_view(title='Pastebin API')
#
# urlpatterns = [
#     path('schema/', schema_view),
# ]
