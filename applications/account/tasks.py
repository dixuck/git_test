from core.celery import app
from applications.account.utils import (
    send_activation_code, send_drop_password_code)
from django.contrib.auth import get_user_model

User = get_user_model()


@app.task
def send_activation_code_task(user_id):
    user = User.objects.get(id=user_id)
    send_activation_code(user)


@app.task
def send_drop_password_code_task(email, code):
    send_drop_password_code(email, code)
