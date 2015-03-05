import hashlib, random
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import Http404 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.forms import UserCreationForm
from forms import MyRegistrationForm
from activation.models import Activating_Data,Reset_Password
from django.contrib import auth

def signup(request):
        if request.method == 'GET':
                form = MyRegistrationForm()
		return	render(request, 'email/signup.html', {'form' : form})
	else:
		try:
                        user = User.objects.get(username=request.POST.get('username'))
	        except (ValueError, ObjectDoesNotExist):
			token_string = request.POST.get('username') + str(random.randint(1000,9999))
			token = hashlib.md5()
			token.update(token_string.encode('utf-8'))
                        link = 'http://'+request.META.get("HTTP_HOST") + reverse('signup_confirm_email')+'?email='+request.POST.get('email')+'&token='+token.hexdigest()
			# send_mail('Welcome To Alertimizer',"Click on url to confirm:\n"+link, 'kanteshraj@gmail.com', [str(request.POST.get('username'))], fail_silently=False)
                        plaintext = get_template('email/confirm_email.txt')
                        htmltext = get_template('email/confirm_email.html')
                        d = Context({ 'confirm_url': link })
                        text_content = plaintext.render(d)
                        html_content = htmltext.render(d)
                        subject = "Confirm Email account - Alertimizer"
                        from_email = "singhanuj115@gmail.com"
                        to = request.POST.get('email')
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        activation = Activating_Data.objects.create(activation_token = token.hexdigest(),activation_password = request.POST.get('password1'),activator_username = request.POST.get('username'))
                        message = "Verification email has been sent.Verify your email id to proceed furthur."
			return render(request, 'email/signup.html',{'message':message,'hide':True})
		else:
                        message = "User already exists. Recover account by reseting password."
			return render(request, 'email/signup.html',{'message':message})



def user_email_confirm(request):
	if request.method == "GET":
		if request.GET.get('email') and	request.GET.get('token'):
                                activation = Activating_Data.objects.get(activation_token = request.GET.get('token'))
                                if request.GET.get('token') == activation.activation_token:
				                user = User.objects.create_user(activation.activator_username,request.GET.get('email'),activation.activation_password )
                                                user.is_active = True
                                                user.save()
                                                d = Context()
                                                plaintext = get_template('email/welcome_mail.txt')
                                                htmltext = get_template('email/welcome_mail.html')
                                                text_content = plaintext.render(d)
                                                html_content = htmltext.render(d)
                                                subject = "Welcome | Alertimizer"
                                                from_email = "welcome@alertimizer.com"
                                                to = request.GET.get('email')
                                                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                                                msg.attach_alternative(html_content, "text/html")
                                                msg.send()
                                                message = "Thank you for confirming your email id.<br>You are in a queue.<br>You will get an activation mail soon."
                                                return render(request, 'email/email_confirm.html',{'message':message})
                message = "Account Verified or Something went wrong. Please contact SUPPORT"
		return render(request, 'email/email_confirm.html',{'message':message})
	else:
		raise Http404

def user_login(request):
	if request.method == "GET":
		if request.user.is_authenticated():
			if request.GET.get("next"):
				return HttpResponseRedirect(request.GET.get("next"))
			else:
				return HttpResponseRedirect('/accounts/loggedin/')
                return render(request, 'login.html',{'next':request.GET.get("next")})
	else:
		next = request.POST.get('next')
		user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
		if user is not None:
			if user.is_active:
				login(request, user)
                                return HttpResponseRedirect('/accounts/loggedin/')
			else:
                                messages.add_message(request, messages.INFO, 'Kindly wait for your account activation')
				return HttpResponseRedirect(reverse('login'))
                else:
                        messages.add_message(request, messages.INFO, 'Username or Password is Incorrect')
			return HttpResponseRedirect(reverse('login'))

def loggedin(request):
    return render(request,'loggedin.html', {'full_name':request.user.username})

def logout(request):
    auth.logout(request)
    return render(request,'loggedout.html',{'full_name':request.user.username})


def password_reset(request):
	if request.method == "GET":
                return render(request, 'email/password_reset.html')
	else:                
		username=request.POST.get('username')
		try:
			user = User.objects.get(username__exact=username)
		except (ValueError, ObjectDoesNotExist):
                        message = "User does not exist"
                        return render(request, 'email/password_reset.html',{'message':message})
		else:
                        plaintext = get_template('email/forgot_password.txt')
                        htmltext = get_template('email/forgot_password.html')
			token_string = username + str(random.randint(100000,999999))
			token = hashlib.md5()
			token.update(token_string.encode('utf-8'))
			link = 'http://'+request.META.get("HTTP_HOST") + reverse('password_reset_confirm')+'?email='+username+'&token='+token.hexdigest()
                        d = Context({ 'reset_url': link })
                        text_content = plaintext.render(d)
                        html_content = htmltext.render(d)
                        subject = "Forgot Password - Alertimizer"
                        from_email = "admin@alertimizer.com"
                        to = user.email
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
			
                        Reset_Password.objects.create(reset_email_token = token.hexdigest())
			message = "Password reset link sent to your email account"
                        return render(request, 'email/password_reset.html',{'message':message})

def password_reset_confirm(request):
	if request.method == "GET":
		if request.GET.get('email') and	request.GET.get('token'):
			reset = Reset_Password.objects.get(reset_email_token = request.GET.get('token'))
			if reset.reset_email_token  == request.GET.get('token'):
				return render(request,'email/password_reset_confirm.html',{"username": request.GET.get('email'),"token": request.GET.get('token')})
		return render(request,'email/password_reset_error.html')
	else:
		print request.META['HTTP_REFERER'] 
		if request.POST.get('new_password') and request.POST.get('reset_token'):
			print request.POST.get('reset_token')
                        print request.GET.get('token') 
			if request.POST.get('reset_token'): 
				user = User.objects.get(username__exact=request.user)
                                user.set_password(request.POST.get('new_password'))
				user.save()
                                messages.add_message(request, messages.INFO, 'Password Reset Done.')
				return HttpResponseRedirect(reverse('logout'))
			return render(request,'email/password_reset_error.html')

