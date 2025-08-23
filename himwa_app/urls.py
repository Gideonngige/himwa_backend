from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('resetpassword/<str:email>/', views.resetpassword, name='resetpassword'),
    path('members/', views.members, name='members'),
    path('create_bill/', views.create_bill, name='create_bill'),
    path('get_all_bills/', views.get_all_bills, name='get_all_bills'),
    path('get_member_bills/<int:member_id>/', views.get_member_bills, name='get_member_bills'),
    path('pay_bill/<int:bill_id>/<int:payment_amount>/<str:payment_method>/<int:member_id>/', views.pay_bill, name='pay_bill'),
    path('get_member_transactions/<int:member_id>/', views.get_member_transactions, name='get_member_transactions'),
    path('get_notifications/<int:member_id>/', views.get_notifications, name='get_notifications'),
    path('send_expo_token/<int:member_id>/<str:expo_token>/', views.send_expo_token, name='send_expo_token'),
    path('updateprofile/', views.updateprofile, name='updateprofile'),
    path("get_water_summary/<int:member_id>/", views.get_water_summary, name="water_summary"),

]
