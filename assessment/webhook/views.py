import json
import secrets
import requests
from django.http import JsonResponse
from .models import Account, Destination
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404



def generate_secret_token():
    return secrets.token_urlsafe(32)


def validate_token(request):
    secret_token = request.headers.get('CL-XTOKEN')
    if not secret_token:
        return None, 'Un Authenticate'

    try:
        account = Account.objects.get(app_secret_token=secret_token)
        return account, None
    except Account.DoesNotExist:
        return None, 'Un Authenticate'


# Create Account
@csrf_exempt
def create_account(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        account_name = data.get('account_name')
        email = data.get('email')
        account_id = data.get('account_id')
        website = data.get('website', '')

        app_secret_token = generate_secret_token()

        account = Account.objects.create(
            account_name=account_name,
            email=email,
            account_id=account_id,
            website=website,
            app_secret_token=app_secret_token
        )

        return JsonResponse({
            'account_id': account.account_id,
            'account_name': account.account_name,
            'app_secret_token': app_secret_token
        }, status=201)

    return JsonResponse({'message': 'Invalid request method'}, status=400)


# Create Destination
@csrf_exempt
def create_destination(request):
    if request.method == 'POST':
        account, error = validate_token(request)
        if error:
            return JsonResponse({'message': error}, status=403)

        data = json.loads(request.body)
        account_id = data.get('account_id')

        if account.account_id != account_id:
            return JsonResponse({'message': 'Account ID mismatch'}, status=400)

        url = data.get('url')
        http_method = data.get('http_method')
        headers = data.get('headers')

        destination = Destination.objects.create(account=account, url=url, http_method=http_method, headers=headers)
        return JsonResponse({'destination_id': destination.id, 'url': destination.url}, status=201)

    return JsonResponse({'message': 'Invalid request method'}, status=400)


def get_destinations(request, account_id):
    account, error = validate_token(request)
    if error:
        return JsonResponse({'message': error}, status=403)

    if account.account_id != account_id:
        return JsonResponse({'message': 'Account ID mismatch'}, status=400)

    destinations = account.destinations.all()
    destinations_list = [{"url": dest.url, "http_method": dest.http_method, "headers": dest.headers} for dest in
                         destinations]
    return JsonResponse({'destinations': destinations_list}, status=200)

# Delete Account and its Destinations
@csrf_exempt
def delete_account(request, account_id):
    if request.method == 'DELETE':
        # Retrieve the account to delete
        account = get_object_or_404(Account, account_id=account_id)

        # Delete the account, which will also delete associated destinations due to cascade
        account.delete()

        return JsonResponse({'message': 'Account and its destinations deleted successfully'}, status=200)

    return JsonResponse({'message': 'Invalid request method'}, status=400)


@csrf_exempt
def incoming_data(request):
    if request.method == 'POST':
        secret_token = request.headers.get('CL-XTOKEN')
        if not secret_token:
            return JsonResponse({'message': 'Un Authenticate'}, status=403)

        try:
            account = Account.objects.get(app_secret_token=secret_token)
        except Account.DoesNotExist:
            return JsonResponse({'message': 'Un Authenticate'}, status=403)

        try:
            data = json.loads(request.body)
        except ValueError:
            return JsonResponse({'message': 'Invalid Data'}, status=400)

        destinations = account.destinations.all()
        for destination in destinations:
            if destination.http_method == 'GET':
                response = requests.get(destination.url, params=data, headers=destination.headers)
            elif destination.http_method == 'POST':
                response = requests.post(destination.url, json=data, headers=destination.headers)
            elif destination.http_method == 'PUT':
                response = requests.put(destination.url, json=data, headers=destination.headers)

        return JsonResponse({'message': 'Data sent to destinations'}, status=200)

    elif request.method == 'GET':

        if request.body:
            try:

                data = json.loads(request.body)
                return JsonResponse({'message': 'Invalid Data'}, status=400)
            except ValueError:

                return JsonResponse({'message': 'Invalid Data'}, status=400)

        return JsonResponse({'message': 'GET request received'}, status=200)

    return JsonResponse({'message': 'Invalid request method'}, status=400)

