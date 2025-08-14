from django.http import JsonResponse
from rest_framework import status


def handler404(request, exception):
    return JsonResponse(
        {'error': 'Page not found', 'message': 'Xatolik'},
        status=status.HTTP_404_NOT_FOUND
    )


def handler500(request):
    return JsonResponse(
        {'error': 'Server error', 'message': 'Ichki server xatoligi yuz berdi.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
