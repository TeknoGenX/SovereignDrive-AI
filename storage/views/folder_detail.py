from .dashboard import dashboard

def folder_detail(request, folder_id):
    return dashboard(request, folder_id)
