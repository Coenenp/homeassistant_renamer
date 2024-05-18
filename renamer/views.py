import csv
import json
import re
import requests
import websocket
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UploadFileForm, RegexForm, UserRegisterForm, AppConfigForm
#from . import config
from .models import AppConfig

TLS_S = ''
HOST = ''
ACCESS_TOKEN = ''

def index(request):
    return render(request, 'renamer/index.html')


def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )

            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = UserRegisterForm()
    
    return render(request, 'renamer/signup.html', {'form': form})


@login_required
def home(request):
    try:
        app_config = AppConfig.objects.get(user=request.user)
        global HOST, ACCESS_TOKEN  # Declare as global to modify their values
        HOST = app_config.host
        ACCESS_TOKEN = app_config.access_token
        tls_enabled = app_config.tls_enabled
    except AppConfig.DoesNotExist:
        # Redirect to configuration form page
        return redirect('config_form')
    
    # Determine the protocol based on TLS configuration
    global TLS_S
    TLS_S = 's' if tls_enabled else ''

    # Header containing the access token
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    upload_form = UploadFileForm()
    regex_form = RegexForm()
    rename_report = []
    entity_data = []
    replace_regex = None
    output_file = None
    rename_data = request.session.get('rename_data', [])

    def handle_result(result_message, rename_data):
        request.session['rename_data'] = rename_data  # Store in session
        if result_message:
            if "err" in result_message.lower():
                messages.error(request, result_message)
            elif "warning" in result_message.lower():
                messages.warning(request, result_message)
            else:
                messages.success(request, f'Other info: {result_message}')

    if request.method == 'GET' and 'clear_results' in request.GET:
            rename_data = []
            entity_data = []
            search_regex = None
            replace_regex = None
            output_file = None
            
    if request.method == 'POST':
        if 'csv_submit' in request.POST:
            upload_form = UploadFileForm(request.POST, request.FILES)
            if upload_form.is_valid():
                input_file = request.FILES.get('input_file')
                output_file = upload_form.cleaned_data.get('output_file')
                result_message, rename_data = process_entities([], None, None, output_file, input_file)
                handle_result(f'Looking Good, proceeding with renaming. {result_message}', rename_data)
                result_message, rename_report = rename_entities(rename_data, request)
                handle_result(f'CSV renaming completed. {result_message}', rename_data)

        elif 'regex_submit' in request.POST:
            regex_form = RegexForm(request.POST)
            if regex_form.is_valid():
                search_regex = regex_form.cleaned_data.get('search_regex')
                replace_regex = regex_form.cleaned_data.get('replace_regex')
                output_file = regex_form.cleaned_data.get('output_file')

                entity_data = list_entities(search_regex, headers)

                if entity_data:
                    messages.success(request, 'Entities listed below.')
                    result_message, rename_data = process_regex_entities(entity_data, search_regex, replace_regex, output_file)
                    handle_result(result_message, rename_data)
                else:
                    rename_data = []
                    messages.error(request, 'No entities found matching the search regex.')

        elif 'rename_confirm' in request.POST:
            rename_data = request.session.get('rename_data', [])
            result_message, rename_report = rename_entities(rename_data, request)
            handle_result(result_message, rename_data)
            del request.session['rename_data']
            rename_data = []

    return render(request, 'renamer/home.html', {
        'upload_form': upload_form,
        'regex_form': regex_form,
        'rename_data': rename_data,
        'replace_regex': replace_regex,
        'rename_report': rename_report
    })


@login_required
def config_form(request):
    if request.method == 'POST':
        form = AppConfigForm(request.POST)
        if form.is_valid():
            # Associate the form data with the current user
            app_config = form.save(commit=False)
            app_config.user = request.user
            app_config.save()
            return redirect('home')  # Redirect back to the home page
    else:
        form = AppConfigForm()

    return render(request, 'renamer/config_form.html', {'form': form})


def list_entities(regex=None, headers=None):
    api_endpoint = f'http{TLS_S}://{HOST}/api/states'
    response = requests.get(api_endpoint, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)
        entity_data = [(entity['attributes'].get('friendly_name', ''), entity['entity_id']) for entity in data]
        
        if regex:
            entity_data = [(friendly_name, entity_id) for friendly_name, entity_id in entity_data if re.search(regex, entity_id)]
        
        return sorted(entity_data, key=lambda x: x[0])
    else:
        raise requests.HTTPError(f'Error: {response.status_code} - {response.text}')


def process_entities(entity_data, search_regex, replace_regex=None, output_file=None, input_filename=None):
    rename_data = []
    required_headers = ['Current Entity ID', 'Friendly Name', 'New Entity ID']
    
    if isinstance(input_filename, InMemoryUploadedFile):
        input_filename.open()
        reader = csv.DictReader(input_filename.read().decode('utf-8').splitlines())
        headers = reader.fieldnames

        missing_headers = [header for header in required_headers if header not in headers]
        if missing_headers:
            return f"Error, missing headers in the input file: {', '.join(missing_headers)}", []

        for row in reader:
            entity_id = row['Current Entity ID']
            friendly_name = row.get('Friendly Name', '')
            new_entity_id = row.get('New Entity ID', '')
            rename_data.append((friendly_name, entity_id, new_entity_id))
        input_filename.close()

        if not rename_data:
            return "Warning, no data found in the input file.", []

    else:
        if replace_regex:
            for friendly_name, entity_id in entity_data:
                try:
                    new_entity_id = re.sub(search_regex, replace_regex, entity_id)
                except re.error as e:
                    return f"Regex error: {e}", []
                rename_data.append((friendly_name, entity_id, new_entity_id))
        else:
            rename_data = [(friendly_name, entity_id, "") for friendly_name, entity_id in entity_data]

    if output_file:
        try:
            table = [("Friendly Name", "Current Entity ID", "New Entity ID")] + rename_data
            write_to_csv(table, output_file)
            return f"Table written to {output_file}", rename_data
        except (PermissionError, IOError) as e:
            return str(e), rename_data

    return "", rename_data


def process_regex_entities(entity_data, search_regex, replace_regex, output_file):
    result_message = ""
    rename_data = []

    if replace_regex and output_file:
        result_message, rename_data = process_entities(entity_data, search_regex, replace_regex, output_file)
    elif replace_regex:
        result_message, rename_data = process_entities(entity_data, search_regex, replace_regex)
    elif output_file:
        result_message, rename_data = process_entities(entity_data, search_regex, None, output_file)
    else:
        result_message, rename_data = process_entities(entity_data, search_regex)
    
    return result_message, rename_data


def rename_entities(rename_data, request):
    rename_report = []
    websocket_url = f'ws{TLS_S}://{HOST}/api/websocket'

    try:
        ws = websocket.WebSocket()
        ws.connect(websocket_url)

        auth_req = ws.recv()

        # Authenticate with Home Assistant
        auth_msg = json.dumps({"type": "auth", "access_token": ACCESS_TOKEN})
        ws.send(auth_msg)
        auth_result = ws.recv()
        auth_result = json.loads(auth_result)
        if auth_result["type"] != "auth_ok":
            return "Error, authentication failed. Check your access token.", rename_report

        for index, (friendly_name, entity_id, new_entity_id) in enumerate(rename_data, start=1):
            entity_registry_update_msg = {
                "id": index,
                "type": "config/entity_registry/update",
                "entity_id": entity_id,
            }
            if new_entity_id:
                entity_registry_update_msg["new_entity_id"] = new_entity_id
            if friendly_name:
                entity_registry_update_msg["name"] = friendly_name

            ws.send(json.dumps(entity_registry_update_msg))
            update_result = json.loads(ws.recv())
            if update_result["success"]:
                success_msg = f"Entity '{entity_id}'"
                if new_entity_id:
                    success_msg += f" renamed to '{new_entity_id}'"
                if friendly_name:
                    success_msg += f" with friendly name '{friendly_name}'"
                success_msg += " successfully!"
                rename_report.append(success_msg)
            else:
                error_message = update_result.get('error', {}).get('message', 'Unknown error')
                rename_report.append(f"Failed to update entity '{entity_id}': {error_message}")

        ws.close()
        return "Renaming completed with details above.", rename_report

    except Exception as e:
        return f"Error, WebSocket connection failed: {e}", rename_report


def write_to_csv(table, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(table)