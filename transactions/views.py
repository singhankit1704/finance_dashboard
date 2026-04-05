from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionSerializer, TransactionCreateUpdateSerializer
from .filters import TransactionFilter
from users.permissions import IsAdmin, IsAnalystOrAdmin, IsAnyRole


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    return Response({"success": True, "message": message, "data": data}, status=status_code)


class TransactionListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/transactions/  - List transactions
        - Admins see all; viewers/analysts see only their own
        - Supports filters: type, category, date_from, date_to, amount_min, amount_max
        - Supports search: description
        - Supports ordering: amount, date
    POST /api/transactions/  - Create a transaction (Admin only)
    """
    filterset_class = TransactionFilter
    search_fields = ['description', 'category']
    ordering_fields = ['amount', 'date', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAnyRole()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TransactionCreateUpdateSerializer
        return TransactionSerializer

    def get_queryset(self):
        qs = Transaction.objects.filter(is_deleted=False)
        # Admins see all records; others see only their own
        if not self.request.user.is_admin:
            qs = qs.filter(user=self.request.user)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            paginated = self.get_paginated_response(serializer.data)
            return Response({"success": True, "message": "Transactions fetched.", "data": paginated.data})
        serializer = TransactionSerializer(queryset, many=True)
        return success_response(serializer.data, "Transactions fetched.")

    def create(self, request, *args, **kwargs):
        serializer = TransactionCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save(user=request.user)
        return success_response(
            TransactionSerializer(transaction).data,
            "Transaction created successfully.",
            status.HTTP_201_CREATED
        )


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/transactions/<id>/  - View a transaction (viewer/analyst/admin)
    PATCH  /api/transactions/<id>/  - Update a transaction (Admin only)
    DELETE /api/transactions/<id>/  - Soft delete a transaction (Admin only)
    """

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdmin()]
        return [IsAnyRole()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TransactionCreateUpdateSerializer
        return TransactionSerializer

    def get_queryset(self):
        qs = Transaction.objects.filter(is_deleted=False)
        if not self.request.user.is_admin:
            qs = qs.filter(user=self.request.user)
        return qs

    def retrieve(self, request, *args, **kwargs):
        transaction = self.get_object()
        return success_response(TransactionSerializer(transaction).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        transaction = self.get_object()
        serializer = TransactionCreateUpdateSerializer(transaction, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(TransactionSerializer(transaction).data, "Transaction updated successfully.")

    def destroy(self, request, *args, **kwargs):
        """Soft delete — marks is_deleted=True instead of removing from DB."""
        transaction = self.get_object()
        transaction.is_deleted = True
        transaction.save()
        return success_response(message="Transaction deleted successfully.")
