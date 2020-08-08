from django.shortcuts import render

# Create your views here.

def gate_security(request):
    
    return render(request, "gate_security.html")

def gate_student(request):
    
    return render(request, "gate_student.html")

