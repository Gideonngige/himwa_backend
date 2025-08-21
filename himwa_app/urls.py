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

]
