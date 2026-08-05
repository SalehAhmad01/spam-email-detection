from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def scan_text(request):
    return render(request, 'detector/scan.html')
