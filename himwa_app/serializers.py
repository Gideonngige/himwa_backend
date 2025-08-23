from rest_framework import serializers
from .models import Notification, Bill

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'member_id', 'message', 'is_read', 'message_type', 'date']

class BillSerializer(serializers.ModelSerializer):
    # Access member fullname through the relationship
    member_fullname = serializers.CharField(source="biller_id.member_id.fullname", read_only=True)

    class Meta:
        model = Bill
        fields = ["id", "member_fullname", "amount", "units", "date", "due_date", "status"]


class BillSummarySerializer(serializers.Serializer):
    total_units = serializers.DecimalField(max_digits=10, decimal_places=2)
    last_recorded = serializers.DateTimeField()