from django.test import TransactionTestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Wallet
from decimal import Decimal
import concurrent.futures
from django.db import connection, transaction
import uuid


class WalletAPITest(APITestCase):
    def setUp(self):
        self.wallet = Wallet.objects.create(balance=Decimal('100.00'))
        self.base_url = f'/api/v1/wallets/'

    def test_create_wallet(self):
        response = self.client.post(self.base_url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['balance'], '0.00')

    def test_get_wallet(self):
        response = self.client.get(f'{self.base_url}{self.wallet.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '100.00')

    def test_deposit(self):
        data = {
            'operation_type': 'DEPOSIT',
            'amount': '50.00'
        }
        response = self.client.post(
            f'{self.base_url}{self.wallet.id}/operation/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['balance']), '150.00')

    def test_withdraw(self):
        data = {
            'operation_type': 'WITHDRAW',
            'amount': '50.00'
        }
        response = self.client.post(
            f'{self.base_url}{self.wallet.id}/operation/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['balance']), '50.00')

    def test_insufficient_funds(self):
        data = {
            'operation_type': 'WITHDRAW',
            'amount': '150.00'
        }
        response = self.client.post(
            f'{self.base_url}{self.wallet.id}/operation/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_deposit(self):
        data = {
            'operation_type': 'DEPOSIT',
            'amount': '-50.00'
        }
        response = self.client.post(
            f'{self.base_url}{self.wallet.id}/operation/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_wallet(self):
        fake_uuid = uuid.uuid4()

        response = self.client.get(f'{self.base_url}{fake_uuid}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Кошелек не найден')

        data = {
            'operation_type': 'DEPOSIT',
            'amount': '50.00'
        }
        response = self.client.post(
            f'{self.base_url}{fake_uuid}/operation/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Кошелек не найден')


class ConcurrencyTest(TransactionTestCase):
    def setUp(self):
        self.wallet = Wallet.objects.create(balance=Decimal('1000.00'))
        self.num_requests = 1000
        self.amount_per_request = Decimal('1.00')

    def tearDown(self):
        connection.close()

    def make_deposit(self):
        try:
            connection.close()
            with transaction.atomic():
                self.wallet.refresh_from_db()
                wallet = Wallet.objects.select_for_update().get(id=self.wallet.id)
                wallet.balance += self.amount_per_request
                wallet.save()
        except Exception as e:
            print(f"Error in make_deposit: {str(e)}")
            raise
        finally:
            connection.close()

    def test_concurrent_deposits(self):
        initial_balance = self.wallet.balance
        expected_balance = initial_balance + \
            (self.amount_per_request * self.num_requests)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for _ in range(self.num_requests):
                future = executor.submit(self.make_deposit)
                futures.append(future)

            concurrent.futures.wait(futures)

            for future in futures:
                if future.exception():
                    print(f"Future exception: {future.exception()}")
                    raise future.exception()

        connection.close()

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, expected_balance)
