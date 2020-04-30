from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from processing.models import Project
from django.shortcuts import (get_object_or_404, 
                              render,
                              redirect, 
                              HttpResponseRedirect)
def register(request):
  if request.method == 'POST':
    # Get form values
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password2 = request.POST['password2']

    # Check if passwords match
    if password == password2:
      # Check username
      if User.objects.filter(username=username).exists():
        messages.error(request, 'That username is taken')
        return redirect('register')
      else:
        if User.objects.filter(email=email).exists():
          messages.error(request, 'That email is being used')
          return redirect('register')
        else:
          # Looks good
          user = User.objects.create_user(username=username, password=password,email=email, first_name=first_name, last_name=last_name)
          # Login after register
          # auth.login(request, user)
          # messages.success(request, 'You are now logged in')
          # return redirect('index')
          user.is_active = False
          user.save()
          messages.success(request, 'You are now registered and can log in')
          return redirect('login')
    else:
      messages.error(request, 'Passwords do not match')
      return redirect('register')
  else:
    return render(request, 'accounts/register.html')

def login(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)

    if user is not None:
      auth.login(request, user)
      messages.success(request, 'You are now logged in')
      return redirect('about')
    else:
      messages.error(request, 'Invalid credentials')
      return redirect('login')
  else:
    return render(request, 'accounts/login.html')

def logout(request):
  if request.method == 'POST':
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('index')

@login_required(login_url='login')
def dash(request):
	projects = Project.objects.filter(user = request.user)
	total_projects = projects.count()
	context = {'projects':projects,
	'total_projects':total_projects }
	return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def deleteProject(request, pk):
  project = Project.objects.get(id=pk)
  creator = project.user.username
  if request.method == "POST" and request.user.is_authenticated and request.user.username == creator:
    project.delete()
    return redirect('dash')
  context = {'project':project}
  return render(request, 'accounts/delete.html', context)

@login_required(login_url='login')
def updateProject(request, pk):
	project = Project.objects.get(id=pk)
	if request.method == "POST":
		project.delete()
		return redirect('dash')

	context = {'project':project}
	return render(request, 'accounts/delete.html', context)

  
''' #def update_view(request, id):
      # dictionary for initial data with  
      # field names as keys 
      context ={} 

      # fetch the object related to passed id 
      obj = get_object_or_404(GeeksModel, id = id) 

      # pass the object as instance in form 
      form = GeeksForm(request.POST or None, instance = obj) 

      # save the data from the form and 
      # redirect to detail_view 
      if form.is_valid(): 
        form.save() 
        return HttpResponseRedirect("/"+id) 

      # add form dictionary to context 
      context["form"] = form 

      return render(request, "update_view.html", context) 

  def listing_update(request, pk):
      instance = get_object_or_404(Listing, pk=pk)
      form = ProductForm(request.POST or None, request.FILES or None, instance=instance)
      if request.user == instance.seller:
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, 'Your Product has been updated successfully')
            return redirect('listings')
      context = {
        'title': instance.title,
        'listing': instance,
        'form': form,
      }
      return render(request, 'listings/update.html', context)    
  '''