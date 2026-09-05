from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, date
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer, BookingCancelSerializer
from .services import get_available_slots
from resources.models import Resource


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or getattr(request.user, 'is_admin_role', False):
            return True
        return obj.user_id == request.user.id


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource', 'status', 'user']
    search_fields = ['title', 'description']
    ordering_fields = ['start_datetime', 'created_at']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = Booking.objects.select_related('resource', 'user', 'resource__category')
        user = self.request.user
        if not user.is_authenticated:
            return qs.filter(resource__is_public=True)
        if not (user.is_staff or getattr(user, 'is_admin_role', False)):
            qs = qs.filter(user=user)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        output = BookingSerializer(booking, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        # Soft cancel instead of hard delete
        instance.cancel(self.request.user, reason='Deleted by user')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        ser = BookingCancelSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            booking.cancel(request.user, reason=ser.validated_data.get('reason', ''))
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(BookingSerializer(booking, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        booking = self.get_object()
        if booking.status != Booking.Status.PENDING:
            return Response({'detail': 'Only pending bookings can be approved.'}, status=400)
        booking.status = Booking.Status.CONFIRMED
        booking.approved_by = request.user
        booking.approved_at = timezone.now()
        booking.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
        return Response(BookingSerializer(booking, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        booking = self.get_object()
        if booking.status != Booking.Status.PENDING:
            return Response({'detail': 'Only pending bookings can be rejected.'}, status=400)
        booking.status = Booking.Status.REJECTED
        booking.cancellation_reason = request.data.get('reason', '')
        booking.cancelled_at = timezone.now()
        booking.cancelled_by = request.user
        booking.save()
        return Response(BookingSerializer(booking, context={'request': request}).data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def calendar(self, request):
        """Return bookings for FullCalendar (start/end query params)."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        resource_id = request.query_params.get('resource')
        qs = Booking.objects.select_related('resource', 'user').filter(
            status__in=[Booking.Status.CONFIRMED, Booking.Status.PENDING],
            resource__is_public=True,
        )
        if start:
            qs = qs.filter(end_datetime__gte=start)
        if end:
            qs = qs.filter(start_datetime__lte=end)
        if resource_id:
            qs = qs.filter(resource_id=resource_id)
        events = []
        for b in qs:
            events.append({
                'id': str(b.id),
                'title': f'{b.title} ({b.resource.name})',
                'start': b.start_datetime.isoformat(),
                'end': b.end_datetime.isoformat(),
                'status': b.status,
                'resourceId': b.resource_id,
                'color': '#2563EB' if b.status == Booking.Status.CONFIRMED else '#D97706',
                'extendedProps': {
                    'description': b.description,
                    'user': b.user.get_full_name() or b.user.username,
                },
            })
        return Response(events)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def available_slots(self, request):
        resource_id = request.query_params.get('resource')
        date_str = request.query_params.get('date')
        if not resource_id or not date_str:
            return Response({'detail': 'resource and date required'}, status=400)
        try:
            resource = Resource.objects.get(pk=resource_id)
            d = date.fromisoformat(date_str)
        except (Resource.DoesNotExist, ValueError):
            return Response({'detail': 'Invalid resource or date'}, status=400)
        slots = get_available_slots(resource, d)
        return Response({'resource': resource.slug, 'date': date_str, 'slots': slots})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user).select_related('resource').order_by('-start_datetime')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

