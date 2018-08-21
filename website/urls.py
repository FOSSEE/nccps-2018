from django.urls import path,include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('proposal', views.proposal, name='proposal'),
    #path('login', views.login, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('proposal/view', views.view_abstracts, name='view_abstracts'),
    path('proposal/submitcfp', views.submitcfp, name='submitcfp'),
    #path('accounts/register', views.userregister, name='userregister'),
]
