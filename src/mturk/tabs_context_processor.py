def tabs(request):


    path = request.path_info

    top_tab = 'start'    
    if path != "/":
        top_tab = path.replace('/','')
    
    return {
        'top_tab':top_tab
    }
    