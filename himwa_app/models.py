from django.db import models

# Create your models here.
class Member(models.Model):
    fullname = models.CharField(max_length=100)
    national_id = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    area_of_residence = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    profile_image = models.URLField(max_length=200, blank=True, null=True, default='https://res.cloudinary.com/dc68huvjj/image/upload/v1748119193/zzy3zwrius3kjrzp4ifc.png')
    expo_token = models.CharField(max_length=200, default="qOE08EA5OCq-yL323EhTY8")
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.fullname} - {self.area_of_residence}'

class Team(models.Model):
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE)
    ROLES = [
        ('Manager', 'Manager'),
        ('Chairperson', 'Chairperson'),
        ('Secretary', 'Secretary'),
        ('Treasurer', 'Treasurer'),
        ('Accountant', 'Accountant'),
        ('Water engineer', 'Water engineer'),
        ('Plumber', 'Plumber')
    ]
    role = models.CharField(max_length=100, choices=ROLES, default='Manager')
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    employment_date = models.DateTimeField(auto_now_add=True)
    CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended')
    ]
    status = models.CharField(max_length=100, choices=CHOICES, default='ACTIVE')

    def __str__(self):
        return f'{self.role} - {self.salary} - {self.status}'

class Bill(models.Model):
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE)
    biller_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('OVERDUE', 'Overdue')
    ]
    status = models.CharField(max_length=100, choices=CHOICES, default='UNPAID')

    def __str__(self):
        return f'{self.member_id.fullname} - {self.amount} - {self.status}'

class Payment(models.Model):
    bill_id = models.ForeignKey(Bill, on_delete=models.CASCADE)
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateTimeField(auto_now_add=True)
    METHODS = [
        ('MOBILE', 'Mobile'),
        ('CASH', 'Cash'),
        ('BANK', 'Bank'),
        ('OTHER', 'Other')

    ]
    payment_method = models.CharField(max_length=100, choices=METHODS, default='MOBILE')

    def __str__(self):
        return f'{self.member} - {self.amount} - {self.payment_method}'   

class Notification(models.Model):
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    is_read = models.BooleanField(default=False)
    MESSAGE_TYPES = [
        ('ALERT', 'Alert'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
    ]
    message_type = models.CharField(max_length=100, choices=MESSAGE_TYPES)
    date = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f'{self.member} - {self.message} - {self.is_read}' 

class Report(models.Model):
    report = models.CharField(max_length=100)
    REPORT_TYPES = [
        ('YEARLY', 'Yearly'),
        ('MONTHLY', 'Monthly'),
        ('WEEKLY', 'Weekly'),
        ('DAILY', 'Daily')
    ]
    report_type = models.CharField(max_length=100, choices=REPORT_TYPES, default='DAILY')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.report_type} - {self.date}'
