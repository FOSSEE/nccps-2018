"""NCCPS2018 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views


urlpatterns = [
    re_path(r'^nccps-2018/', include('website.urls', namespace='website')),
    re_path(r'^nccps-2018/accounts/',
            include(('django.contrib.auth.urls', 'auth'), namespace='auth')),
    path('nccps-2018/admin/', admin.site.urls),

    re_path(r'^', include('social.apps.django_app.urls', namespace='social')),

    re_path(r'^nccps-2018/forgotpassword/$', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'), name="password_reset"),
    re_path(r'^nccps-2018/password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    re_path(r'^nccps-2018/password_reset/mail_sent/$', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
            name='password_reset_done'),
    re_path(r'^nccps-2018/password_reset/complete/$', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
            name='password_reset_complete'),
    re_path(r'^nccps-2018/changepassword/$', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'),
            name='password_change'),
    re_path(r'^nccps-2018/password_change/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
            name='password_change_done'),
]