from django.shortcuts import redirect

def redirect_from_base(request):
    return redirect('/swagger/')
