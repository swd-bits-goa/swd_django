from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth.models import User

# from main.forms import HomeForm
from main.models import Student

def index(request):
    return render(request, 'home.html',{})

class HomeView(TemplateView):
    template_name = 'home/home.html'

    def get(self, request):
        # form = HomeForm()
        # posts = Post.objects.all().order_by('-created')
        users = User.objects.exclude(id=request.user.id)
        student = Student.objects.get(user=request.user)
        # friends = friend.users.all()

        args = {
            'student': student, 'users': users, 
        }
        return render(request, self.template_name, args)

    def post(self, request):
        form = HomeForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            text = form.cleaned_data['post']
            form = HomeForm()
            return redirect('main:main')

        args = {'form': form, 'text': text}
        return render(request, self.template_name, args)

def login_success(request):
    return HttpResponse("Success!")
