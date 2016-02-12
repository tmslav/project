import ujson
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.views.generic import TemplateView

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .celery_tasks import submit_csv as add_to_queue
from .models import DetailModel, Results
from django.http import JsonResponse
from app_aws_db.models import DetailsItem

USERNAME = 'test'
PASSWORD = 'test123'


class Login(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login/index.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['u']
        password = request.POST['p']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/app")
        else:
            return render(request, 'login/index.html')


class Main(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return render(request, 'app/index.html')
        else:
            return redirect('/')


@csrf_exempt
def upload(request):
    if request.method == 'POST':
        csv = request.FILES.get('name', None)
        search_name = request.POST['search_name']
        if csv:
            add_to_queue(csv.readlines(), search_name)
            return redirect("/app")
        else:
            return redirect("/app")


def items(request, id):
    if request.method == 'GET':
        ret = {'items': []}
        items = Results.objects.get(resultid=id)
        ret['search_name'] = items.search_name
        ret['timestamp'] = items.timestamp
        items = items.detailmodel_set.all() if items else None
        for item in items:
            ret['items'].append(
                {'timestamp': item.timestamp, 'part_id': item.part_id, 'url': item.url, 'status': item.status,
                 'site_name': item.site_name})
        return JsonResponse(ret)


def results(request):
    ret = {'results': []}
    items = Results.objects.all()
    keys = map(lambda x: x.attname, Results._meta.fields)
    for item in items:
        ret['results'].append({k: getattr(item, k) for k in keys})
    return JsonResponse(ret)


def last(request, number):
    ret = {'last' + str(number): []}
    keys = map(lambda x: x.attname, DetailsItem._meta.fields)
    items = DetailsItem.objects.order_by('-id')[:int(number)][::-1]
    for item in items:
        ret['last' + str(number)].append({k: getattr(item, k) for k in keys})
    return JsonResponse(ret)

def logout_1(request):
    logout(request)
    return redirect("/")
