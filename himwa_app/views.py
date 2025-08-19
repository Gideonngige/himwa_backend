from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import pyrebase
import json


firebase_config = {
    "apiKey": "AIzaSyCvXvn5T3gvhw4b0DHgowI5KHGgbmkvh1M",
    "authDomain": "g-tech-6fc99.firebaseapp.com",
    "databaseURL": "https://g-tech-6fc99-default-rtdb.firebaseio.com/",
    "projectId": "g-tech-6fc99",
    "storageBucket": "g-tech-6fc99.firebasestorage.app",
    "messagingSenderId": "522681202970",
    "appId": "1:522681202970:web:eaae59ec9c054cb85f54a3",
    "measurementId": "G-NS7RN7JB3B"
}
firebase = pyrebase.initialize_app(firebase_config)
authe = firebase.auth() 
database = firebase.database()

import firebase_admin
from firebase_admin import auth, credentials
import os, json

# Initialize Firebase once (e.g., in settings.py or a startup file)
# os.environ["FIREBASE_SERVICE_ACCOUNT"]
# service_account_info = json.loads('./firebase_key.json')
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

def verify_firebase_token(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"message": "Unauthorized"}, status=401)
        
        token = auth_header.split(" ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
            # You can attach UID and email from token to the request for easy access
            request.user_uid = decoded_token.get("uid")
            request.user_email = decoded_token.get("email")
        except Exception as e:
            return JsonResponse({"message": "Invalid or expired token", "error": str(e)}, status=401)
        
        return view_func(request, *args, **kwargs)
    return wrapper

def index(request):
    return HttpResponse("Hello world!")


