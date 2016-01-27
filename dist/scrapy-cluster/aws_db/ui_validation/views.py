from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import login,authenticate
from django.views.generic import TemplateView
USERNAME = 'test'
PASSWORD = 'test123'

# Create your views here.
class Login(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login/index.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['u']
        password = request.POST['p']
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect("/app")
        else:
            return render(request,'login/index.html')

class Main(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return render(request,'app/index.html')
        else:
            return redirect('/')

