from django.urls import path

from apps.accounts.api.v1 import views

urlpatterns = [
    path('register', views.RegisterByPhoneNumber.as_view()),
    path('verify', views.VerifyCode.as_view()),
    path('complete', views.CompleteUserInfo.as_view()),
    path('complete/password', views.CompleteUserPassword.as_view()),
    path('login', views.LoginUser.as_view()),
]
