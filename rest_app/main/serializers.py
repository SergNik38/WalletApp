from rest_framework import serializers
from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance']


class OperationSerializer(serializers.Serializer):
    OPERATION_CHOICES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
    ]
    operation_type = serializers.ChoiceField(choices=OPERATION_CHOICES)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
