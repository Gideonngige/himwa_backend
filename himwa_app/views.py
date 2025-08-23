from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import pyrebase
import json
from .models import Member, Bill, Team, Payment, Notification
from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from rest_framework.response import Response
from .serializers import NotificationSerializer, BillSerializer, BillSummarySerializer
import cloudinary.uploader
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.db.models import Sum, Max


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
# firebase_admin.initialize_app(cred)
if not firebase_admin._apps:
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
    return render(request, 'index.html')

#start of signin api
@api_view(['POST'])
def signin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"message": "Email and password are required"}, status=400)

            member = authe.sign_in_with_email_and_password(email, password)
            
            if Member.objects.filter(email=email).exists():
                session_id = member['idToken']
                request.session['uid'] = str(session_id)
                get_member = Member.objects.filter(email=email).first()
                member_id = get_member.id
                member_name = get_member.fullname
                phonenumber = get_member.phonenumber
                area_of_residence = get_member.area_of_residence
                profile_image = get_member.profile_image
                joined_date = get_member.joined_date
                return JsonResponse({"message": "Successfully logged in", "member_id":member_id, "member_name":member_name,"member_email":email,"phonenumber":phonenumber, "area_of_resident":area_of_residence, "profile_image":profile_image, "date_joined":joined_date, "token":session_id}, status=200)
            else:
                return JsonResponse({"message": "No user found with this email, please register"}, status=404)

        except Exception as e:
            print("Error:", str(e))  # Optional logging
            return JsonResponse({"message": "Invalid credentials. Please check your email and password."}, status=401)

    return JsonResponse({"message": "Invalid request method"}, status=405)
#end of signin api

# signup api
@api_view(['POST'])
def signup(request):
    try:
        fullname = request.data.get("fullname")
        national_id = request.data.get("national_id")
        phonenumber = request.data.get("phonenumber")
        email = request.data.get("email")
        area_of_residence = request.data.get("area_of_residence")
        password = request.data.get("password")

        print(area_of_residence)

        # Check if email already exists
        if Member.objects.filter(email=email).exists():
            return JsonResponse({"message": "An account with this email already exists"}, status=400)


        # Create Firebase user
        user = authe.create_user_with_email_and_password(email, password)
        uid = user['localId']

        # Save Member
        member = Member(
            fullname=fullname,
            national_id=national_id,
            phonenumber=phonenumber,
            email=email,
            area_of_residence=area_of_residence,
            password=uid,
        )
        member.save()

        return JsonResponse({"message": "Successfully registered"}, status=201)

    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({"message": "Registration failed", "error": str(e)}, status=500)
#end of signUp api

#end of reset api
def resetpassword(request, email):
    try:
        authe.send_password_reset_email(email)
        message = "A email to reset password is successfully sent"
        return JsonResponse({"message": message})
    except:
        message = "Something went wrong, Please check the email, provided is registered or not"
        return JsonResponse({"message": message})
#start of reset api

# api to get all members
@api_view(['GET'])
@verify_firebase_token
def members(request):
    try:
        members = Member.objects.all().values(
            "id",
            "fullname",
            "national_id",
            "phonenumber",
            "email",
            "area_of_residence",
            "profile_image",
            "expo_token",
            "joined_date",
        )
        return JsonResponse(list(members), safe=False, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# api to create a bill
@api_view(['POST'])
@verify_firebase_token
def create_bill(request):
    try:
        member_id = request.data.get("member_id")
        biller_id = request.data.get("biller_id")
        units = request.data.get("units")
        due_date = request.data.get("due_date")

        # Check if member and team exist
        member = Member.objects.get(id=member_id)
        biller = Team.objects.get(id=biller_id)

        amount = units * 20

        bill = Bill.objects.create(
            member_id=member,
            biller_id=biller,
            units=units,
            amount=amount,
            due_date=due_date,
        )

        return JsonResponse({
            "message": "Bill created successfully",
            "bill_id": bill.id,
            "member": member.fullname,
            "amount": bill.amount,
            "status": bill.status,
            "due_date": bill.due_date
        }, status=201)

    except ObjectDoesNotExist as e:
        return JsonResponse({"error": str(e)}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#Get all bills
@api_view(['GET'])
@verify_firebase_token
def get_all_bills(request):
    try:
        bills = Bill.objects.all().values(
            "id",
            "member_id__fullname",
            "biller_id__member_id__fullname",
            "amount",
            "date",
            "due_date",
            "status"
        )
        return JsonResponse(list(bills), safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#Get bills for a specific member
@api_view(['GET'])
@verify_firebase_token
def get_member_bills(request, member_id):
    try:
        member = Member.objects.get(id=member_id)
        bills = Bill.objects.filter(member_id=member)
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Member.DoesNotExist:
        return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@verify_firebase_token
def pay_bill(request, bill_id, payment_amount, payment_method, member_id ):
    try:

        if not payment_amount or not member_id:
            return JsonResponse({"error": "amount and member_id are required"}, status=400)

        payment_amount = Decimal(payment_amount)

        if payment_amount <= 0:
            return JsonResponse({"error": "Invalid payment amount"}, status=400)

        bill = Bill.objects.get(id=bill_id)
        member = Member.objects.get(id=member_id)

        # Create Payment transaction 
        payment = Payment.objects.create(
            bill_id=bill,
            member_id=member,
            amount=payment_amount,
            payment_method=payment_method
        )

        # Update bill progress
        bill.amount_paid += payment_amount

        # Check if fully paid
        if bill.amount_paid >= bill.amount:
            bill.status = "PAID"
            bill.amount_paid = bill.amount  # cap at total amount
        else:
            bill.status = "UNPAID"

        bill.save()

        return JsonResponse({
            "message": "Payment processed successfully",
            "bill_id": bill.id,
            "bill_total": bill.amount,
            "amount_paid": bill.amount_paid,
            "remaining_balance": bill.amount - bill.amount_paid,
            "status": bill.status,
            "payment": {
                "payment_id": payment.id,
                "amount": str(payment.amount),
                "method": payment.payment_method,
                "date": payment.date
            }
        }, status=201)

    except Bill.DoesNotExist:
        return JsonResponse({"error": "Bill not found"}, status=404)
    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
@verify_firebase_token
def get_member_transactions(request, member_id):
    try:
        transactions = Payment.objects.filter(member_id=member_id).values(
            "id",
            "bill_id",
            "amount",
            "payment_method",
            "date"
        )

        return JsonResponse(list(transactions), safe=False, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# api to get notifications for a member
@api_view(['GET'])
@verify_firebase_token
def get_notifications(request, member_id):
    notifications = Notification.objects.filter(member_id=member_id).order_by('-date')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

# api to send_expo_token to database
@api_view(['GET'])
@verify_firebase_token
def send_expo_token(request, member_id, expo_token):
    try:
        member = Member.objects.get(id=member_id)
        member.expo_token = expo_token
        member.save()
        return JsonResponse({"message":"Token saved successfully"})

    except Member.DoesNotExist:
        return JsonResponse({"message": "Member not found"}, status=404)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


# start of update profile api
@api_view(['POST'])
@parser_classes([MultiPartParser])
@verify_firebase_token
def updateprofile(request):
    try:
        member_id = request.data.get('member_id')
        member_name = request.data.get('member_name')
        phonenumber = request.data.get('phonenumber')
        area_of_residence = request.data.get('area_of_residence')
        profile_image = request.FILES.get('profile_image', None)

        member = Member.objects.get(id=member_id)

        if member_name:
            member.fullname = member_name
        if phonenumber:
            member.phonenumber = phonenumber
        if area_of_residence:
            member.area_of_residence = area_of_residence
        
        image_url = None
        if profile_image:
            upload_result = cloudinary.uploader.upload(profile_image)
            image_url = upload_result.get("secure_url")
            member.profile_image = image_url  # Assuming this is an ImageField

        member.save()
        return JsonResponse({"message": "ok"})

    except Member.DoesNotExist:
        return JsonResponse({"message": "Member not found"}, status=404)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)

# end of update profile api

@api_view(["GET"])
@verify_firebase_token
def get_water_summary(request, member_id):
    try:
        # Check if member exists
        member = Member.objects.get(id=member_id)

        # Aggregate total units and last recorded bill date
        data = Bill.objects.filter(member_id=member).aggregate(
            total_units=Sum("units"),
            last_recorded=Max("date")
        )

        if not data["total_units"]:
            return Response(
                {"message": "No water consumption records found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BillSummarySerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Member.DoesNotExist:
        return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)