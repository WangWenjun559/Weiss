from django.shortcuts import render

# Create your views here.
def homepage(request):
    context = {}

    return render(request,'testapp/index.html',context)

def showNumber(request):
    number = 5

    context = {}
    context['number'] = number

    return render(request, 'testapp/index.html', context)
