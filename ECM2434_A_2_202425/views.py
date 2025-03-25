from django.http import JsonResponse

def api_config(request):
    """Return API configuration to the frontend."""
    base_url = request.build_absolute_uri('/').rstrip('/')
    return JsonResponse({
        'apiBaseUrl': f"{base_url}/api/"
    })

