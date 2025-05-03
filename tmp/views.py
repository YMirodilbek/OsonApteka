from django.shortcuts import render

# Create your views here.


def Operator(request):
    return render(request,'new/operator.html')


def Vacancy(request):
    return render(request,'new/vacancy.html')


def Pharm(request):
    return render(request,'new/farmaset.html')


def About(request):
    return render(request,'new/onas.html')


def Policy(request):
    return render(request,'new/politka.html')

def Conditions(request):
    return render(request,'new/vozvarat.html')

def Public(request):
    return render(request,'new/oferta.html')


def Resipe(request):
    return render(request,'new/zagruske-svet.html')


def Landlords(request):
    return render(request,'new/arendatelim.html')

def Vacancies(request):
    return render(request,'new/farmaset.html')

