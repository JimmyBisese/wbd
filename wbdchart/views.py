from django.http import HttpResponse
from django.shortcuts import render_to_response

def IndexChart (request):
    return render_to_response('templates/index.html')