from django.urls import path
from applications.account.views import (
    NewUserView, ChangePasswordView, UserView,
    ActivationView, DropPasswordView, ChangeForgottenPasswordView
    )

urlpatterns = [
    path('create-account/', NewUserView.as_view(), name='create-account'),
    path(
        'change-password/', ChangePasswordView.as_view(),
        name='change-password'
        ),
    path('users/', UserView.as_view()),
    path('activate/', ActivationView.as_view(), name='activation'),
    path('drop-password/', DropPasswordView.as_view(), name='drop-password'),
    path(
        'set-new-password/', ChangeForgottenPasswordView.as_view(),
        name='set-new-password'
        ),
]
