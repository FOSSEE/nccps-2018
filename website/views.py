# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response, render, redirect
from django.template import loader
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import (csrf_exempt, csrf_protect,
                                          ensure_csrf_cookie,
                                          requires_csrf_token)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from website.models import (Proposal, Comments, Ratings, Question,
                            AnswerPaper, Profile)

from website.forms import (ProposalForm, UserRegisterForm, UserRegistrationForm,
                           UserLoginForm, WorkshopForm,QuestionUploadForm
                           )# ,ContactForm
from website.models import Proposal, Comments, Ratings
from social.apps.django_app.default.models import UserSocialAuth
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, date
from django import template
from django.core.mail import EmailMultiAlternatives
import os
from nccps2018.config import *
from website.send_mails import send_email
from django.contrib.auth.models import Group
from django.contrib import messages



def is_email_checked(user):
    if hasattr(user, 'profile'):
        return True if user.profile.is_email_verified else False
    else:
        return False


def is_superuser(user):
    return True if user.is_superuser else False


def index(request):
    context = {}
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

def cfp(request):
    context = {}
    template = loader.get_template('cfp.html')
    return HttpResponse(template.render(context, request))

def dwsimquiz(request):
    context = {}
    template = loader.get_template('dwsim-quiz.html')
    return HttpResponse(template.render(context, request))
    
# def proposal(request):
#    context = {}
#    template = loader.get_template('proposal.html')
#    return HttpResponse(template.render(context, request))


@csrf_protect
def proposal(request):
    if request.method == "POST":
        context = {}
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if 'next' in request.GET:
                next = request.GET.get('next', None)
                return HttpResponseRedirect(next)
            proposals = Proposal.objects.filter(user=request.user).count()
            context['user'] = user
            context['proposals'] = proposals
            template = loader.get_template('proposal.html')
            return HttpResponse(template.render(context, request))
        else:
            context['invalid'] = True
            context['form'] = UserLoginForm
            context['user'] = user
            template = loader.get_template('proposal.html')
            return HttpResponse(template.render(context, request))
    else:
        form = UserLoginForm()
        context = {'request': request,
                   'user': request.user,
                   'form': form,
                   }
        template = loader.get_template('proposal.html')
        return HttpResponse(template.render(context, request))

# User Register
@csrf_protect
def userregister(request):
    context = {}
    registered_emails = []
    users = User.objects.all()
    for user in users:
        registered_emails.append(user.email)
    if request.user.is_anonymous:
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data['email'] in registered_emails:
                    context['form'] = form
                    context['email_registered'] = True
                    return render_to_response('registration/signup.html', context)
                else:
                    form.save()
                    context['registration_complete'] = True
                    form = UserLoginForm()
                    context['form'] = form
                    context['user'] = request.user
                    template = loader.get_template('cfp.html')
                    return HttpResponse(template.render(context, request))
            else:

                context['form'] = form
                template = loader.get_template('user-register.html')
                return HttpResponse(template.render(context, request))
        else:
            form = UserRegisterForm()
        context['form'] = form
        template = loader.get_template('user-register.html')
        return HttpResponse(template.render(context, request))
    else:
        context['user'] = request.user
        template = loader.get_template('user-register.html')
        return HttpResponse(template.render(context, request))

# View Proposal/Paper


@login_required
@csrf_protect
def view_abstracts(request):
    user = request.user
    context = {}
    count_list = []
    if request.user.is_authenticated:
        if user.is_staff:
            proposals = Proposal.objects.all().order_by('status')
            ratings = Ratings.objects.all()
            context['ratings'] = ratings
            context['proposals'] = proposals
            context['user'] = user
            return render(request, 'view-proposals.html', context)
        elif user is not None:
            if Proposal.objects.filter(user=user).exists:
                proposals = Proposal.objects.filter(
                    user=user).order_by('status')
                proposal_list = [pro.proposal_type for pro in proposals]
                if 'WORKSHOP' in proposal_list and 'PAPER' in proposal_list:
                    proposal_type = 'BOTH'
                elif 'WORKSHOP' in proposal_list and 'PAPER' not in proposal_list:
                    proposal_type = 'WORKSHOP'
                else:
                    proposal_type = 'PAPER'

                context['counts'] = count_list
                context['proposals'] = proposals
                context['type'] = proposal_type
                context['user'] = user
            return render(request, 'view-proposals.html', context)
        else:
            return render(request, 'cfp.html')
    else:
        return render(request, 'cfp.html', context)


@requires_csrf_token
def user_login(request):
    user = request.user
    if request.user.is_authenticated:
        return redirect('/nccps-2018/proposal/')
    else:
        if request.method == "POST":
            context = {}
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)
            user = authenticate(username=username, password=password)
            #proposals_a = Proposal.objects.filter(
            #    user=request.user, proposal_type='PAPER').count()
            if user is not None:
                login(request, user)
                proposals = Proposal.objects.filter(user=request.user).count()
                context['user'] = user
                return redirect('/nccps-2018/proposal')
                #template = loader.get_template('index.html')
                #return render(request, 'index.html', context)
            else:
                context['invalid'] = True
                context['form'] = UserLoginForm
                context['user'] = user
                #context['proposals_a'] = proposals_a
                return render(request, 'login.html', context)
        else:
            form = UserLoginForm()
            context = {'request': request,
                       'user': request.user,
                       'form': form,
                       }
            template = loader.get_template('login.html')
            return HttpResponse(template.render(context, request))


@csrf_protect
@login_required
def submitcfp(request):
    context = {}
    if request.user.is_authenticated:
        social_user = request.user

        django_user = User.objects.get(username=social_user)
        context['user'] = django_user
        proposals_a = Proposal.objects.filter(
            user=request.user, proposal_type='PAPER').count()
        if request.method == 'POST':
            form = ProposalForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                data.user = django_user
                data.email = social_user.email
                data.save()
                context['proposal_submit'] = True
                sender_name = "NCCPS 2018"
                sender_email = TO_EMAIL
                subject = "NCCPS 2018 – Paper Submission Acknowledgement "
                to = (social_user.email, TO_EMAIL)
                message = """
                Dear {0}, <br><br>
                Thank you for showing interest & submitting a paper proposal at NCCPS-2018 
                for the paper titled "<b>{1}</b>". Reviewal of the proposals will start 
                once the CFP closes.
                You will be notified regarding comments/selection/rejection of your paper via email. 
                Visit this {2} link to view the status of your submission.
                <br>Thank You. <br><br>Regards,<br>NCCPS 2018,<br>FOSSEE - IIT Bombay.
                """.format(
                    social_user.first_name,
                    request.POST.get('title', None),
                    'https://dwsim.fossee.in/nccps-2018/view-abstracts/',)
                email = EmailMultiAlternatives(
                    subject, '',
                    sender_email, to,
                    headers={"Content-type": "text/html;charset=iso-8859-1"}
                )
                email.attach_alternative(message, "text/html")
                email.send(fail_silently=True)
                return render_to_response('proposal.html', context)
            else:
                context['proposal_form'] = form
                context['proposals_a'] = proposals_a
                template = loader.get_template('submit-cfp.html')
                return HttpResponse(template.render(context, request))
        else:
            form = ProposalForm()
            context['proposals_a'] = proposals_a
            return render(request, 'submit-cfp.html', {'proposal_form': form})
    else:
        context['login_required'] = True
        return render_to_response('login.html', context)


@csrf_protect
@login_required
def submitcfw(request):
    context = {}
    if request.user.is_authenticated:
        social_user = request.user
        # context.update(csrf(request))
        django_user = User.objects.get(username=social_user)
        context['user'] = django_user
        proposals_w = Proposal.objects.filter(
            user=request.user, proposal_type='WORKSHOP').count()
        if request.method == 'POST':
            form = WorkshopForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                data.user = django_user
                data.email = social_user.email
                data.save()
                context['proposal_submit'] = True
                sender_name = "NCCPS 2018"
                sender_email = TO_EMAIL
                subject = "NCCPS 2018 – Workshop Proposal Submission Acknowledgment"
                to = (social_user.email, TO_EMAIL)
                message = """
                Dear {0}, <br><br>
                Thank you for showing interest & submitting a workshop proposal at NCCPS 2018 conference for the workshop titled <b>“{1}”</b>. Reviewal of the proposals will start once the CFP closes.
                <br><br>You will be notified regarding comments/selection/rejection of your workshop via email.
                Visit this {2} link to view status of your submission.
                <br>Thank You ! <br><br>Regards,<br>NCCPS 2018,<br>FOSSEE - IIT Bombay.
                """.format(
                    social_user.first_name,
                    request.POST.get('title', None),
                    'https://dwsim.fossee.in/nccps-2018/view-abstracts/',)
                email = EmailMultiAlternatives(
                    subject, '',
                    sender_email, to,
                    headers={"Content-type": "text/html;charset=iso-8859-1"}
                )
                email.attach_alternative(message, "text/html")
                # email.send(fail_silently=True)
                return render_to_response('cfp.html', context)
            else:
                context['proposal_form'] = form
                context['proposals_w'] = proposals_w
                template = loader.get_template('submit-cfw.html')
                return HttpResponse(template.render(context, request))

        else:
            form = WorkshopForm()
            context['proposal_form'] = form
            context['proposals_w'] = proposals_w
        template = loader.get_template('submit-cfw.html')
        return HttpResponse(template.render(context, request))
    else:
        context['login_required'] = True
        template = loader.get_template('cfp.html')
        return HttpResponse(template.render(context, request))


@csrf_exempt
def gallery(request):
    return render(request, 'gallery.html')


@login_required
def edit_proposal(request, proposal_id=None):
    user = request.user
    context = {}
    if user.is_authenticated:
        try:
            proposal = Proposal.objects.get(id=proposal_id)
            if proposal.status == 'Edit':
                if proposal.proposal_type == 'PAPER':
                    form = ProposalForm(instance=proposal)
                else:
                    form = WorkshopForm(instance=proposal)
            else:
                return render(request, 'cfp.html')
            if request.method == 'POST':
                if proposal.status == 'Edit':
                    if proposal.proposal_type == 'PAPER':
                        form = ProposalForm(
                            request.POST, request.FILES, instance=proposal)
                    else:
                        form = WorkshopForm(
                            request.POST, request.FILES, instance=proposal)
                else:
                    return render(request, 'cfp.html')
                if form.is_valid():
                    data = form.save(commit=False)
                    data.user = user
                    proposal.status = 'Resubmitted'
                    data.save()
                    context.update(csrf(request))
                    proposals = Proposal.objects.filter(
                        user=user).order_by('status')
                    context['proposals'] = proposals
                    return render(request, 'view-proposals.html', context)
                else:
                    context['user'] = user
                    context['form'] = form
                    context['proposal'] = proposal
                    return render(request, 'edit-proposal.html', context)
            context['user'] = user
            context['form'] = form
            context['proposal'] = proposal
        except:
            render(request, 'cfp.html')
    return render(request, 'edit-proposal.html', context)


@login_required
def abstract_details(request, proposal_id=None):
    user = request.user
    context = {}
    if user.is_authenticated:
        if user.is_superuser:
            proposals = Proposal.objects.all()
            context['proposals'] = proposals
            context['user'] = user
            return render(request, 'cfp.html', context)
        elif user is not None:
            try:
                proposal = Proposal.objects.get(id=proposal_id)
                if proposal.user == user:
                    try:
                        url = '/nccps-2018'+str(proposal.attachment.url)
                        context['url'] = url
                    except:
                        pass
                    comments = Comments.objects.filter(proposal=proposal)
                    context['proposal'] = proposal
                    context['user'] = user
                    context['comments'] = comments
                    path, filename = os.path.split(str(proposal.attachment))
                    context['filename'] = filename
                    return render(request, 'abstract-details.html', context)
                else:
                    return render(request, 'cfp.html', context)
            except:
                return render(request, 'cfp.html', context)
        else:
            return render(request, 'cfp.html', context)
    else:
        return render(request, 'cfp.html', context)


@login_required
def rate_proposal(request, proposal_id=None):
    user = request.user
    context = {}
    if user.is_authenticated:
        proposal = Proposal.objects.get(id=proposal_id)
        if request.method == 'POST':
            ratings = Ratings.objects.filter(
                proposal_id=proposal_id, user_id=user.id)
            if ratings:
                for rate in ratings:
                    rate.rating = request.POST.get('rating', None)
                    rate.save()
            else:
                newrate = Ratings()
                newrate.rating = request.POST.get('rating', None)
                newrate.user = user
                newrate.proposal = proposal
                newrate.save()
            rates = Ratings.objects.filter(proposal_id=proposal_id)
            comments = Comments.objects.filter(proposal=proposal)
            context['comments'] = comments
            context['proposal'] = proposal
            context['rates'] = rates
            # context.update(csrf(request))
            return render(request, 'comment-abstract.html', context)
        else:
            rates = Ratings.objects.filter(proposal=proposal)
            comments = Comments.objects.filter(proposal=proposal)
            context['comments'] = comments
            context['proposal'] = proposal
            context['rates'] = rates
            # context.update(csrf(request))
            return render(request, 'comment-abstract.html', context)
    else:
        return render(request, 'comment-abstract.html', context)


@login_required
def comment_abstract(request, proposal_id=None):
    user = request.user
    context = {}
    if user.is_authenticated:
        if user.is_staff:
            try:
                proposal = Proposal.objects.get(id=proposal_id)
                try:
                    url = '/nccps-2018'+str(proposal.attachment.url)
                    context['url'] = url
                except:
                    pass
                if request.method == 'POST':
                    comment = Comments()
                    comment.comment = request.POST.get('comment', None)
                    comment.user = user
                    comment.proposal = proposal
                    comment.save()
                    comments = Comments.objects.filter(proposal=proposal)
                    sender_name = "NCCPS 2018"
                    sender_email = TO_EMAIL
                    to = (proposal.user.email, TO_EMAIL)
                    if proposal.proposal_type == 'PAPER':
                        subject = "NCCPS 2018 - Comment on Your talk Proposal"
                        message = """
                            Dear {0}, <br><br>
                            There is a comment posted on your proposal titled <b>{1}</b>.<br> 
                            Log in to the website to view comments on your submission.<br><br>
                            Thank You ! <br><br>Regards,<br>NCCPS 2018,<br>FOSSEE - IIT Bombay.
                            """.format(
                            proposal.user.first_name,
                            proposal.title,
                        )
                    email = EmailMultiAlternatives(
                        subject, '',
                        sender_email, to,
                        headers={"Content-type": "text/html;charset=iso-8859-1"}
                    )
                    email.attach_alternative(message, "text/html")
                    email.send(fail_silently=True)
                    proposal.status = "Commented"
                    proposal.save()
                    rates = Ratings.objects.filter(proposal=proposal)
                    context['rates'] = rates
                    context['proposal'] = proposal
                    context['comments'] = comments
                    path, filename = os.path.split(str(proposal.attachment))
                    context['filename'] = filename
                    # context.update(csrf(request))
                    template = loader.get_template('comment-abstract.html')
                    return HttpResponse(template.render(context, request))
                else:
                    comments = Comments.objects.filter(proposal=proposal)
                    rates = Ratings.objects.filter(proposal=proposal)
                    context['rates'] = rates
                    context['proposal'] = proposal
                    context['comments'] = comments
                    path, filename = os.path.split(str(proposal.attachment))
                    context['filename'] = filename
                    # context.update(csrf(request))
                    template = loader.get_template('comment-abstract.html')
                    return HttpResponse(template.render(context, request))
            except:
                template = loader.get_template('cfp.html')
                return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template('cfp.html')
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('abstract-details.html')
        return HttpResponse(template.render(context, request))


@login_required
def status(request, proposal_id=None):
    user = request.user
    context = {}
    if user.is_authenticated:
        if user.is_staff:
            proposal = Proposal.objects.get(id=proposal_id)
            if 'accept' in request.POST:
                proposal.status = "Accepted"
                proposal.save()
                sender_name = "NCCPS 2018"
                sender_email = TO_EMAIL
                to = (proposal.user.email, TO_EMAIL)
                if proposal.proposal_type == 'PAPER':
                    subject = "NCCPS 2018 - Talk Proposal Accepted"
                    message = """Dear """+proposal.user.first_name+""",
                    Thank you for your excellent submissions!  This year we received many really good submissions.  Due the number and quality of the talks this year we have decided to give 20 minute slots to all the accepted talks.  So even though you may have submitted a 30 minute one, we are sorry you will only have 20 minutes.  Of these 20 minutes please plan to do a 15 minute talk (we will strive hard to keep to time), and keep 5 minutes for Q&A and transfer.  We will have the next speaker get ready during your Q&A session in order to not waste time.
                    Pardon the unsolicited advice but it is important that you plan your presentations carefully. 15 minutes is a good amount of time to communicate your central idea. Most really good TED talks finish in 15 minutes.  Keep your talk focussed and please do rehearse your talk and slides to make sure it flows well. If you need help with this, the program chairs can try to help you by giving you some early feedback on your slides.  Just upload your slides before 26th on the same submission interface and we will go over it once.  For anything submitted after 26th we may not have time to comment on but will try to give you feedback.  Please also keep handy a PDF version of your talk in case your own laptops have a problem.
                    Please confirm your participation.  The schedule will be put up online by end of day.  We look forward to hearing your talk.
                    \n\nYou will be notified regarding instructions of your talk via email.\n\nThank You ! \n\nRegards,\nNCCPS 2018,\nFOSSEE - IIT Bombay"""
                elif proposal.proposal_type == 'WORKSHOP':
                    subject = "NCCPS 2018 - Workshop Proposal Accepted"
                    message = """Dear """+proposal.user.first_name+""",
                    Thank you for your excellent submissions!  We are pleased to accept your workshop. Due to the large number of submissions we have decided to accept 8 workshops and give all the selected workshops 2 hours each. Please plan for 1 hour and 55 minutes in order to give the participants a 10 minute break between workshops for tea.
                    The tentative schedule will be put up on the website shortly.  Please do provide detailed instructions for the participants (and the organizers if they need to do something for you) in your reply.  Please also confirm your participation.
                    We strongly suggest that you try to plan your workshops carefully and focus on doing things hands-on and not do excessive amounts of theory.  Try to give your participants a decent overview so they can pick up additional details on their own. It helps to pick one or two overarching problems you plan to solve and work your way through the solution of those. 
                    Installation is often a problem, so please make sure your instructions are simple and easy to follow.  If you wish, we could allow some time the previous day for installation help.  Let us know about this.  Also, do not waste too much time on installation during your workshop.
                    \n\nYou will be notified regarding instructions of your talk via email.\n\nThank You ! \n\nRegards,\nNCCPS 2018,\nFOSSEE - IIT Bombay"""
                #send_mail(subject, message, sender_email, to)
                # context.update(csrf(request))
            elif 'reject' in request.POST:
                proposal.status = "Rejected"
                proposal.save()
                sender_name = "NCCPS 2018"
                sender_email = TO_EMAIL
                to = (proposal.user.email, TO_EMAIL, )
                if proposal.proposal_type == 'PAPER':
                    subject = "NCCPS 2018 - Paper Proposal Rejected"
                    message = """
                    Dear {0}, <br><br>
                    We are thankful for your submission and patience. 
                    We regret to inform you that your paper titled <b>“{1}”</b> is not selected for NCCPS-2018. 
                    Please check the feedback of reviewers by logging in at {2}.<br>
                    You are welcome to attend the conference. Please register at {3}
                    <br>Thank You ! <br><br>Regards,<br>NCCPS 2018,<br>FOSSEE - IIT Bombay.
                    """.format(
                        proposal.user.first_name,
                        proposal.title,
                        'https://dwsim.fossee.in/nccps-2018/accounts/login/'
                        'https://dwsim.fossee.in/nccps-2018/#registration',)

                elif proposal.proposal_type == 'WORKSHOP':
                    subject = "NCCPS 2018 - Workshop Proposal Rejected"
                    message = """Dear """+proposal.user.first_name+""",
                    Thank you for your submission to the conference. 
                    Unfortunately, due to the large number of excellent workshops submitted, yours was not selected. We hope you are not discouraged and request you to kindly attend the conference and participate. We have an excellent line up of workshops (8 in total) and many excellent talks. You may also wish to give a lightning talk (a short 5 minute talk) at the conference if you so desire. 
                    We look forward to your active participation in the conference.
                    \n\nThank You ! \n\nRegards,\nNCCPS 2018,\nFOSSEE - IIT Bombay"""
                   # message = """Dear """+proposal.user.first_name+""",
                  # Thank you for your excellent workshop submission titled “Digital forensics using Python”.  The program committee was really excited about your proposal and thought it was a very good one.  While the tools you use are certainly in the NCCPS toolstack the application was not entirely in the domain of the attendees we typically have at NCCPS.  This along with the fact that we had many really good workshops that were submitted made it hard to select your proposal this time -- your proposal narrowly missed out.  We strongly suggest that you submit this to other more generic Python conferences like the many PyCon and PyData conferences as it may be a much better fit there.  We also encourage you to try again next year and if we have a larger audience, we may have space for it next year.  This year with two tracks we already have 8 excellent workshops selected.

                    # We really hope you are not discouraged as it was indeed a very good submission and a rather original one at that.  We hope you understand and do consider participating in the conference anyway.

                    # We look forward to seeing you at the conference and to your continued interest and participation.
                    # \n\nRegards,\n\nNCCPS Program chairs"""

                #send_mail(subject, message, sender_email, to)
                # context.update(csrf(request))
            elif 'resubmit' in request.POST:
                to = (proposal.user.email, TO_EMAIL)
                sender_name = "NCCPS 2018"
                sender_email = TO_EMAIL
                if proposal.proposal_type == 'PAPER':
                    subject = "NCCPS 2018 - Talk Proposal Resumbmission"
                    message = """
                    Dear {0}, <br><br>
                    Thank you for your excellent submissions!  Your talk has been accepted! This year we received many really good submissions.  Due to the number and quality of the talks this year we have decided to give 20 minute slots to all the accepted talks.  So even though you may have submitted a 30 minute one, we are sorry you will only have 20 minutes.  Of these 20 minutes please plan to do a 15 minute talk (we will strive hard to keep to time), and keep 5 minutes for Q&A and transfer.  We will have the next speaker get ready during your Q&A session in order to not waste time.
                    Pardon the unsolicited advice but it is important that you plan your presentations carefully. 15 minutes is a good amount of time to communicate your central idea. Most really good TED talks finish in 15 minutes.  Keep your talk focussed and please do rehearse your talk and slides to make sure it flows well. 
                    We (the program chairs) are happy to help you by giving you some early feedback on your slides.  Just upload your slides before 26th and we will go over it once.  You may upload your slides by clicking on edit when you login to the site.  You may also modify your abstract if you want to improve it.  For anything submitted after 26th we may not have time to comment but will try to give you feedback.  Please also keep handy a PDF version of your talk in case your own laptops have a problem.
                    Please confirm your participation via return email.  The tentative schedule will be put up online by end of day.  We look forward to hearing your talk.

                    """.format(
                        proposal.user.first_name,
                        proposal.title,
                        'http://dwsim.fossee.in/nccps-2018/view-abstracts/'
                    )
                elif proposal.proposal_type == 'WORKSHOP':
                    subject = "NCCPS 2018 - Workshop Proposal Resubmission"
                    message = """
                    Thank you for showing interest & submitting a workshop proposal at NCCPS 2018 conference for the workshop titled <b>"{1}"</b>. You are requested to submit this talk proposal once        again.<br>
                    You will be notified regarding comments/selection/rejection of your workshop via email.
                    Visit this {2} link to view comments on your submission.<br><br>
                    Thank You ! <br><br>Regards,<br>NCCPS 2018,<br>FOSSEE - IIT Bombay.
                    """.format(
                        proposal.user.first_name,
                        proposal.title,
                        'http://dwsim.fossee.in/nccps-2018/view-abstracts/'
                    )
                email = EmailMultiAlternatives(
                    subject, '',
                    sender_email, to,
                    headers={"Content-type": "text/html;charset=iso-8859-1"}
                )
                email.attach_alternative(message, "text/html")
                email.send(fail_silently=True)
                proposal.status = "Edit"
                proposal.save()
                # context.update(csrf(request))
        else:
            return render(request, 'view-proposals.html')
    else:
        return render(request, 'view-proposals.html')
    proposals = Proposal.objects.all().order_by('status')
    context['proposals'] = proposals
    context['user'] = user
    return render(request, 'view-proposals.html', context)


@login_required
def status_change(request):
    user = request.user
    context = {}
    if user.is_authenticated:
        if user.is_staff:
            if 'delete' in request.POST:
                delete_proposal = request.POST.getlist('delete_proposal')
                for proposal_id in delete_proposal:
                    proposal = Proposal.objects.get(id=proposal_id)
                    proposal.delete()
                # context.update(csrf(request))
                proposals = Proposal.objects.all()
                context['proposals'] = proposals
                context['user'] = user
                template = loader.get_template('view-proposals.html')
                return HttpResponse(template.render(context, request))
            elif 'dump' in request.POST:
                delete_proposal = request.POST.getlist('delete_proposal')
                blank = False
                if delete_proposal == []:
                    blank = True
                try:
                    if blank == False:
                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="Proposals.csv"'
                        writer = csv.writer(response)
                        header = [
                            'name',
                            'username',
                            'email',
                            'about_me',
                            'phone',
                            'title',
                            'abstract',
                            'prerequisite',
                            'duration',
                            'attachment',
                            'date_created',
                            'status',
                            'proposal_type',
                            'tags',
                        ]
                        writer.writerow(header)
                        for proposal_id in delete_proposal:
                            proposal = Proposal.objects.get(id=proposal_id)
                            row = [
                                '{0} {1}'.format(
                                    proposal.user.first_name, proposal.user.last_name),
                                proposal.user.username,
                                proposal.user.email,
                                proposal.about_me,
                                proposal.phone,
                                proposal.title,
                                proposal.abstract,
                                proposal.prerequisite,
                                proposal.duration,
                                proposal.attachment,
                                proposal.date_created,
                                proposal.status,
                                proposal.proposal_type,
                                proposal.tags,
                            ]
                            writer.writerow(row)
                        return response
                    else:
                        proposals = Proposal.objects.all()
                        context['proposals'] = proposals
                        context['user'] = user
                        template = loader.get_template('view-proposals.html')
                        return HttpResponse(template.render(context, request))
                except:
                    proposals = Proposal.objects.all()
                    context['proposals'] = proposals
                    context['user'] = user
                    template = loader.get_template('view-proposals.html')
                    return HttpResponse(template.render(context, request))
            elif 'accept' in request.POST:
                delete_proposal = request.POST.getlist('delete_proposal')
                for proposal_id in delete_proposal:
                    proposal = Proposal.objects.get(id=proposal_id)
                    proposal.status = "Accepted"
                    proposal.save()
                    sender_name = "NCCPS 2018"
                    sender_email = TO_EMAIL
                    to = (proposal.user.email, TO_EMAIL)
                    if proposal.proposal_type == 'PAPER':
                        subject = "NCCPS 2018 - Talk Proposal Accepted"
                        message = """Dear """+proposal.user.first_name+""",
                        Thank you for your excellent submissions!  This year we received many really good submissions.  Due the number and quality of the talks this year we have decided to give 20 minute slots to all the accepted talks.  So even though you may have submitted a 30 minute one, we are sorry you will only have 20 minutes.  Of these 20 minutes please plan to do a 15 minute talk (we will strive hard to keep to time), and keep 5 minutes for Q&A and transfer.  We will have the next speaker get ready during your Q&A session in order to not waste time.
                    Pardon the unsolicited advice but it is important that you plan your presentations carefully. 15 minutes is a good amount of time to communicate your central idea. Most really good TED talks finish in 15 minutes.  Keep your talk focussed and please do rehearse your talk and slides to make sure it flows well. If you need help with this, the program chairs can try to help you by giving you some early feedback on your slides.  Just upload your slides before 26th on the same submission interface and we will go over it once.  For anything submitted after 26th we may not have time to comment on but will try to give you feedback.  Please also keep handy a PDF version of your talk in case your own laptops have a problem.
                    Please confirm your participation.  The schedule will be put up online by end of day.  We look forward to hearing your talk.
                    \n\nYou will be notified regarding instructions of your talk via email.\n\nThank You ! \n\nRegards,\nNCCPS 2018,\nFOSSEE - IIT Bombay"""
                    #email = EmailMultiAlternatives(
                    #    subject, '',
                    #    sender_email, to,
                    #    headers={"Content-type": "text/html;charset=iso-8859-1"}
                    #)
                    #email.attach_alternative(message, "text/html")
                    #email.send(fail_silently=True)
                proposals = Proposal.objects.all()
                context['proposals'] = proposals
                context['user'] = user
                template = loader.get_template('view-proposals.html')
                return HttpResponse(template.render(context, request))
            elif 'reject' in request.POST:
                delete_proposal = request.POST.getlist('delete_proposal')
                for proposal_id in delete_proposal:
                    proposal = Proposal.objects.get(id=proposal_id)
                    proposal.status = "Rejected"
                    proposal.save()
                    sender_name = "NCCPS 2018"
                    sender_email = TO_EMAIL
                    to = (proposal.user.email, TO_EMAIL)
                    if proposal.proposal_type == 'PAPER':
                        subject = "NCCPS 2018 - Paper proposal result"
                        message = """
                    Dear {0}, <br><br>
                    We are thankful for your submission and patience. 
                    We regret to inform you that your paper titled <b>“{1}”</b> is not selected for NCCPS-2018. 
                    Please check the feedback of reviewers by logging in at {2}.<br>
                    You are welcome to attend the conference. Please register at {3}
                    <br>Thank You ! <br><br>Regards,<br>NCCPS 2018,<br>FOSSEE - IIT Bombay.
                    """.format(
                        proposal.user.first_name,
                        proposal.title,
                        'https://dwsim.fossee.in/nccps-2018/accounts/login/',
                        'https://dwsim.fossee.in/nccps-2018/#registration',)
                    email = EmailMultiAlternatives(
                        subject, '',
                        sender_email, to,
                        headers={"Content-type": "text/html;charset=iso-8859-1"}
                    )
                    email.attach_alternative(message, "text/html")
                    email.send(fail_silently=True)

                proposals = Proposal.objects.all()
                context['proposals'] = proposals
                context['user'] = user
                template = loader.get_template('view-proposals.html')
                return HttpResponse(template.render(context, request))
            elif 'resubmit' in request.POST:
                delete_proposal = request.POST.getlist('delete_proposal')
                for proposal_id in delete_proposal:
                    proposal = Proposal.objects.get(id=proposal_id)
                    sender_name = "NCCPS 2018"
                    sender_email = TO_EMAIL
                    to = (proposal.user.email, TO_EMAIL)
                    if proposal.proposal_type == 'PAPER':
                        subject = "NCCPS 2018 - Talk Proposal Acceptance"
                        message = """
                        Dear {0}, <br><br>
                        Thank you for your excellent submissions!  Your talk has been accepted! This year, we have received many really good submissions.  Due to the number and quality of the talks this year we have decided to give 20 minute slots to all the accepted talks.  So even though you may have submitted a 30 minute one, we are sorry you will only have 20 minutes.  Of these 20 minutes, please plan to do a 15 minute talk (we will strive hard to keep to time), and keep 5 minutes for Q&A and transfer.  We will have the next speaker get ready during your Q&A session in order to not waste time.

Pardon the unsolicited advice but it is important that you plan your presentations carefully. 15 minutes is a good amount of time to communicate your central idea. Most really good TED talks finish in 15 minutes.  Keep your talk focussed and please do rehearse your talk and slides to make sure it flows well. 

We (the program chairs) are happy to help you by giving you some early feedback on your slides.  Just upload your slides before 26th and we will go over it once.  You may upload your slides by clicking on edit when you login to the site.  You may also modify your abstract if you want to improve it.  For anything submitted after 26th we may not have time to comment but will try to give you feedback.  Please also keep handy a PDF version of your talk in case your own laptops have a problem.

Please confirm your participation via return email.  The tentative schedule will be put up online by end of day.  We look forward to hearing your talk.
Thank You ! <br><br>Regards,<br>NCCPS 2018,<br>FOSSEE - IIT Bombay.
                        """.format(
                            proposal.user.first_name,
                            proposal.title,
                            'http://dwsim.fossee.in/nccps-2018/view-abstracts/'
                        )
                    elif proposal.proposal_type == 'WORKSHOP':
                        subject = "NCCPS 2018 - Workshop Proposal Resubmission"
                        message = """
                        Thank you for showing interest & submitting a workshop proposal at NCCPS 2018 conference for the workshop titled <b>"{1}"</b>. You are requested to submit this talk proposal once        again.<br>
                        You will be notified regarding comments/selection/rejection of your workshop via email.
                        Visit this {2} link to view comments on your submission.<br><br>
                        Thank You ! <br><br>Regards,<br>NCCPS 2018,<br>FOSSEE - IIT Bombay.
                        """.format(
                            proposal.user.first_name,
                            proposal.title,
                            'http://dwsim.fossee.in/nccps-2018/view-abstracts/'
                        )
                    email = EmailMultiAlternatives(
                        subject, '',
                        sender_email, to,
                        headers={"Content-type": "text/html;charset=iso-8859-1"}
                    )
                    email.attach_alternative(message, "text/html")
                    email.send(fail_silently=True)
                    proposal.status = "Edit"
                    proposal.save()
                    # context.update(csrf(request))
                proposals = Proposal.objects.all()
                context['proposals'] = proposals
                context['user'] = user
                template = loader.get_template('view-proposals.html')
                return HttpResponse(template.render(context, request))
            else:
                proposals = Proposal.objects.all()
                context['proposals'] = proposals
                context['user'] = user
                template = loader.get_template('view-proposals.html')
                return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template('cfp.html')
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('view-proposals.html')
        return HttpResponse(template.render(context, request))


@login_required
def edit_proposal(request, proposal_id=None):
    user = request.user
    context = {}
    if user.is_authenticated:
        try:
            proposal = Proposal.objects.get(id=proposal_id)
            if proposal.status == 'Edit':
                if proposal.proposal_type == 'PAPER':
                    form = ProposalForm(instance=proposal)
                else:
                    form = WorkshopForm(instance=proposal)
            else:
                return render(request, 'cfp.html')
            if request.method == 'POST':
                if proposal.status == 'Edit':
                    if proposal.proposal_type == 'PAPER':
                        form = ProposalForm(
                            request.POST, request.FILES, instance=proposal)
                    else:
                        form = WorkshopForm(
                            request.POST, request.FILES, instance=proposal)
                else:
                    return render(request, 'cfp.html')
                if form.is_valid():
                    data = form.save(commit=False)
                    data.user = user
                    proposal.status = 'Resubmitted'
                    data.save()
                    context.update(csrf(request))
                    proposals = Proposal.objects.filter(
                        user=user).order_by('status')
                    context['proposals'] = proposals
                    return render(request, 'view-abstracts.html', context)
                else:
                    context['user'] = user
                    context['form'] = form
                    context['proposal'] = proposal
                    return render(request, 'edit-proposal.html', context)
            context['user'] = user
            context['form'] = form
            context['proposal'] = proposal
        except:
            template = loader.get_template('cfp.html')
            return HttpResponse(template.render(context, request))
    template = loader.get_template('edit-proposal.html')
    return HttpResponse(template.render(context, request))


@csrf_exempt
def contact_us(request, next_url):
    pass
    # user = request.user
    # context = {}
    # if request.method == "POST":
    #     form = ContactForm(request.POST)
    #     sender_name = request.POST['name']
    #     sender_email = request.POST['email']
    #     to = ('nccps@fossee.in',)
    #     subject = "Query from - "+sender_name
    #     message = request.POST['message']
    #     try:
    #         send_mail(subject, message, sender_email, to)
    #         context['mailsent'] = True
    #         context['user'] = user
    #     except:
    #         context['mailfailed'] = True
    #         context['user'] = user
    # return redirect(next_url,context)


@csrf_protect
def user_register(request):
    '''User Registration form'''
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username, password, key = form.save()
            new_user = authenticate(username=username, password=password)
            login(request, new_user)
            user_position = request.user.profile.position
            send_email(
                request, call_on='Registration',
                user_position=user_position,
                key=key
            )

            return render(request, 'view-profile.html')
        else:
            if request.user.is_authenticated:
                return redirect('/nccps-2018/view_profile/')
            return render(
                request, "user-register.html",
                {"form": form}
            )
    else:
        if request.user.is_authenticated and is_email_checked(request.user):
            return redirect('/nccps-2018/view_profile/')
        elif request.user.is_authenticated:
            return render(request, 'activation.html')
        form = UserRegistrationForm()
    return render(request, "user-register.html", {"form": form})


@csrf_protect
@login_required
def view_profile(request):
    """ view instructor and coordinator profile """
    user = request.user
    if is_superuser(user):
        return redirect('/admin')
    if is_email_checked(user) and user.is_authenticated:
        return render(request, "view-profile.html")
    else:
        if user.is_authenticated:
            return render(request, 'view-profile.html')
        else:
            try:
                logout(request)
                return redirect('/login/')
            except:
                return redirect('/register/')

"""@csrf_protect
@login_required
def question_add(request):
    context = {}
    if request.user.is_authenticated:
        social_user = request.user

        django_user = User.objects.get(username=social_user)
        context['user'] = django_user
        if request.method == 'POST':
            form = QuestionForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.user = django_user
                data.email = social_user.email
                data.save()
                return render_to_response('question-display.html', context)
                return HttpResponse(template.render(context, request))
            else:
                context['qform'] = form
                template = loader.get_template('question-display.html')
                return HttpResponse(template.render(context, request))
        else:
            form = QuestionForm()
            return render(request, 'question-display.html', {'qform': form})
    else:
        context['login_required'] = True
        return render_to_response('login.html', context)

@csrf_protect
def quiz_view(request):
    context = {}
    if request.user.is_authenticated:
        social_user = request.user
        django_user = User.objects.get(username=social_user)
        questions = Question.objects.all()
        context['user'] = django_user
        context['questions'] = questions
        template = loader.get_template('quiz-display.html')
        return HttpResponse(template.render(context, request))
    else:
        context['login_required'] = True
        return render_to_response('login.html', context)
"""


def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@login_required
def question_list(request):
    user = request.user
    grouptype = Group.objects.get(name='moderator')
    if has_group(user, grouptype):
        question_list = Question.objects.all()
        return render(request, 'question_list.html', {'question_list': question_list})
    else:
        logout(request)
        return redirect('/nccps-2018/accounts/login/')


@login_required
def add_questions(request):
    user = request.user
    if request.method == 'POST':
        form = QuestionUploadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question Uploaded Successfully! .')
        else:
            return redirect('/nccps-2018/add_questions')

    grouptype = Group.objects.get(name='moderator')
    if has_group(user, grouptype):
        question_form = QuestionUploadForm()
        return render(request, 'add_question.html', {'questions': question_form})
    else:
        logout(request)
        return redirect('/nccps-2018/accounts/login/')


@login_required
def edit_question(request, qid=None):
    """ edit profile details facility for instructor and coordinator """

    user = request.user
    context = {'template': template}
    if request.method == 'POST':
        form = QuestionUploadForm(request.POST)
        if form.is_valid():
            form.save()
            return render(
                        request, 'add_question.html'
                        )
        else:
            context['form'] = form
            return render(request, 'add_question.html', context)
    else:
        question = Question.objects.get(id=qid)
        form = QuestionUploadForm(instance=question)
        return render(request, 'edit_question.html', {'form': form})


@login_required
def quiz_intro(request):
    return render(request, 'quiz_intro.html')

@login_required
def take_quiz(request):
    user = request.user
    today = datetime.today().date()
    question_list = Question.objects.filter(question_day=today)
    user_profile = Profile.objects.get(user_id=user.profile.user_id)
    questions = dict(enumerate(question_list))

    if request.method == 'POST':
        data = request.body.decode("utf-8").split('&')
        if len(data) <3:
            messages.info(request, 'Please answer both the questions!')
        else:
            ans1 = data[1].split("=on")[0].replace("+", ' ').replace("%2F", "/")
            ans2 = data[2].split("=on")[0].replace("+", ' ').replace("%2F", "/")
            ans1 = ans1.split("q1=")[1]
            ans2 = ans2.split("q2=")[1]

            #For First Answer
            ans1_obj = AnswerPaper()
            ans1_obj.participant = user_profile
            ans1_obj.answered_q = questions[0]

            try:
                question1 = AnswerPaper.objects.get(
                                answered_q=questions[0],
                                participant_id=user_profile.id)
                question2 = AnswerPaper.objects.get(
                                answered_q=questions[1],
                                participant_id=user_profile.id)
            except:
                if questions[0].correct_answer==ans1:
                    ans1_obj.validate_ans = 1
                else:
                    ans1_obj.validate_ans = 0
                ans1_obj.save()

                #For Second Answer    
                ans2_obj = AnswerPaper()
                ans2_obj.participant = user_profile
                ans2_obj.answered_q = questions[1]
                if questions[1].correct_answer==ans2:
                    ans2_obj.validate_ans = 1
                else:
                    ans2_obj.validate_ans = 0
                ans2_obj.save()
                messages.info(request, "Submitted Successfully!")

                return redirect('/nccps-2018/take_quiz/')

            if question1 or question2:
                messages.info(request, "You've already taken the quiz")    

    else:
        
        try:
            question1 = AnswerPaper.objects.get(
                                answered_q=questions[0],
                                participant_id=user_profile.id)
            question2 = AnswerPaper.objects.get(
                                answered_q=questions[1],
                                participant_id=user_profile.id)
            
            if question1 or question2:
                questions = None
        except:
            pass

    return render(request, 'take_quiz.html', {
            'question_list' : questions
            })


def leaderboard(request):
    profiles = Profile.objects.all()
    leaderboard = {p:0 for p in profiles}
    marks = {
        '5': [date(2018, 10, 29), date(2018, 11, 4)],
        '10': [date(2018, 11, 5), date(2018, 11, 12)]
        }
    answers = AnswerPaper.objects.all()

    for i in leaderboard:
        profiles = AnswerPaper.objects.filter(participant=i)
        for p in profiles:
            if p.validate_ans==1:
                if marks['5'][0] <= p.answered_q.question_day <= marks['5'][1]:
                    leaderboard[i] +=5
                elif marks['10'][0] <= p.answered_q.question_day <= marks['10'][1]:
                    leaderboard[i] +=10
                else:
                    leaderboard[i] +=1

                
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda kv: kv[1])
    return render(request, "leaderboard.html", {'leaderboard': sorted_leaderboard[::-1]})


'''
@login_required
def uploadmodel(request):
    if request.method == 'POST':
        data = request.body.decode("utf-8").split('&')
        date = data[1].replace("qdate=", "")
        date = datetime.strptime(date, "%Y-%m-%d").date()
        question_list = Question.objects.all()
        try:
            question_obj = Question.objects.get(question_day=date)
            print(question_obj)
            messages.info(request, 'Uploaded Successfully!')
        except:
            messages.error(request, 'No question uploaded for mentioned date')
        
        
        form = UploadModelForm(request.POST)
        if form.is_valid():
            uploadForm = form.save(commit=False)
            try:
                question_obj = Question.objects.get(question_day=date)
                uploadForm.question = question_obj
                uploadForm.model_file
                uploadForm.save()
                messages.info(request, 'Uploaded Successfully!')
            except:
                messages.error(request, 'No question uploaded for mentioned date')
            print(question_obj)
        else:
            messages.error(request, 'Invalid Form')
        

    return render(request, "uploadmodel.html", {"question_list":question_list})'''
    