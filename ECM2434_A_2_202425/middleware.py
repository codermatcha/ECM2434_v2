class APIRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if request is to a localhost API endpoint
        if 'localhost:8000' in request.path:
            # Rewrite the path to remove the localhost part
            request.path = request.path.replace('localhost:8000', '')
            request.path_info = request.path_info.replace('localhost:8000', '')
        
        return self.get_response(request)
