from django.db import models
import secrets


def generate_app_secret_token():
    return secrets.token_hex(32)

class Account(models.Model):
    email = models.EmailField(unique=True)
    account_id = models.CharField(max_length=255, unique=True)
    account_name = models.CharField(max_length=255)
    app_secret_token = models.CharField(max_length=255, unique=True, editable=False, default=generate_app_secret_token)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.account_name

class Account(models.Model):
    email = models.EmailField(unique=True)
    account_id = models.CharField(max_length=255, unique=True)
    account_name = models.CharField(max_length=255)
    app_secret_token = models.CharField(max_length=255, unique=True, editable=False)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.account_name


class Destination(models.Model):
    account = models.ForeignKey(Account, related_name='destinations', on_delete=models.CASCADE)
    url = models.URLField()
    http_method = models.CharField(max_length=10, choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT')])
    headers = models.JSONField()

    def __str__(self):
        return f"Destination for {self.account.account_name}"


class DataHandler(models.Model):
    account = models.ForeignKey(Account, related_name='data_handlers', on_delete=models.CASCADE)
    data = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Data for {self.account.account_name} received at {self.received_at}"
