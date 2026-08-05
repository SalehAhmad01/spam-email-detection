from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def message_list(request):
    return render(request, 'inbox/list.html')
