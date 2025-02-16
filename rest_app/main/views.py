import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db import transaction
from .models import Wallet
from .serializers import WalletSerializer, OperationSerializer
from django.http import Http404


class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise Http404('Кошелек не найден')

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            if 'Неверный формат идентификатора' in str(exc):
                return Response(
                    {'error': str(exc)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'error': str(exc)},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().handle_exception(exc)

    @action(detail=True, methods=['post'], url_path='operation')
    def operation(self, request, pk=None):
        try:
            try:
                uuid.UUID(self.kwargs.get('pk'))
            except (ValueError, AttributeError):
                return Response({'error': 'Неверный формат идентификатора'}, status=status.HTTP_400_BAD_REQUEST)
            wallet = get_object_or_404(Wallet, pk=pk)
        except Http404:
            return Response(
                {'error': 'Кошелек не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OperationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        operation_type = serializer.validated_data['operation_type']
        amount = Decimal(serializer.validated_data['amount'])

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=pk)

            if operation_type == 'DEPOSIT':
                if amount < 0:
                    return Response(
                        {'error': 'Сумма депозита не может быть отрицательной'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                wallet.balance += amount
            elif operation_type == 'WITHDRAW':
                if wallet.balance < amount:
                    return Response(
                        {'error': 'Недостаточно средств'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                wallet.balance -= amount
            else:
                return Response(
                    {'error': 'Неверный тип операции'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            wallet.save()
            return Response({'balance': wallet.balance})
