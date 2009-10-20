def tabs(request):

    top_tab = 'start'
    path = request.path_info

    if path.startswith('/general'):
        top_tab = 'general'        
    
    return {
        'top_tab':top_tab
    }
    