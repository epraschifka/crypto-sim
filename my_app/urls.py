from django.urls import path, re_path
from . import views

urlpatterns = [
    path("login/", views.LoginView, name="login"),
    path("register/", views.RegisterView, name="register"),
    path("logout/", views.LogoutView, name="logout"),
    path("dashboard/", views.DashboardView, name="dashboard"),
    path("data/", views.DataView, name="data"),
    path("coin/<str:pk>", views.CoinView, name="coin"),
    path("",views.BaseView, name="base"),
    re_path(r'^.*$', views.handler404, name="404"),
]