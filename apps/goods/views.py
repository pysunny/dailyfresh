from django.shortcuts import render
from django.views.generic import View
# Create your views here.
# Create your views here.

# http://127.0.0.1:8000
class IndexView(View):
    '''首页'''
    def get(self, request):
        '''显示首页'''
        return render(request, 'index.html')