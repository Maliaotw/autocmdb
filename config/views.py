import logging

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from asset import models as asset_models
from host import models as host_models

logger = logging.getLogger(__name__)



class DashBoardView(View):
    template_name = 'dashboard2.html'

    def get(self, request):
        counts = {
            'asset': asset_models.Asset.objects.all().count(),
            'server': asset_models.Asset.objects.filter(device_type_id=1).count(),
            'netware': asset_models.Asset.objects.filter(device_type_id=2).count(),
            'host': host_models.Host.objects.all().count(),

        }

        return render(request, 'dashboard2.html', locals())


class DashAssetView(APIView):

    def recent_seven_days(self):
        import datetime
        from django.utils import timezone
        today = timezone.now().date()
        # lists = []
        for i in range(7):
            # lists.append(date.strftime('%Y-%m-%d'))
            yield today - datetime.timedelta(days=i)

    def get(self, request):

        logger.info(f'recent_seven_days {self.recent_seven_days()}')
        list_week_day = list(self.recent_seven_days())
        list_week_day.reverse()

        latest_list = []
        create_list = []
        for d in list_week_day:
            latest_list.append(host_models.Host.objects.filter(cate=2, latest_date__date=d).count())

        for d in list_week_day:
            create_list.append(host_models.Host.objects.filter(cate=2, create_at__date=d).count())

        data = {
            'label': [i.strftime('%Y-%m-%d') for i in list_week_day],
            'latest_data': latest_list,
            'create_data': create_list,
        }

        return Response(data)


class DashRackView(APIView):

    def get(self, request):
        rack_obj = asset_models.Rack.objects.all()

        data = {'label': [], 'data': []}
        for r in rack_obj:
            data['data'].append(sum([i.size for i in r.asset_set.all()]))
            data['label'].append(r.name)
        return Response(data)


def acc_login(request):
    error_msg = ""

    if request.method == 'GET':

        # 判斷是否已登入
        if request.user.is_authenticated():
            return redirect(request.GET.get('next', '/asset'))

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)

            return redirect(request.GET.get('next', '/asset'))

        else:
            error_msg = "使用者或密碼有誤!!"

        logger.info(f'{user}, {username}, {password}')

    return render(request, 'login.html', {'error_msg': error_msg})


def acc_logout(request):
    logout(request)
    logger.info("logout")
    return redirect('/login')
