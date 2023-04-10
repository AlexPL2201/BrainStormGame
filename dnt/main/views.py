from django.shortcuts import render


def index(request):
    context = {
        'title': 'Home',
    }
    return render(request, 'main/index.html', context=context)

