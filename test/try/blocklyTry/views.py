from django.shortcuts import HttpResponse, render
from django.template import loader
def editor(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())
