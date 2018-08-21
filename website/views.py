# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from website.models import Proposal, Comments, Ratings
from website.forms import ProposalForm
#UserRegisterForm, UserLoginForm, WorkshopForm, ContactForm


def index(request):
    context = {}
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

def proposal(request):
    context = {}
    template = loader.get_template('proposal.html')
    return HttpResponse(template.render(context, request))

## User Register

def userregister(request):
    context = {}
    registered_emails = []
    users = User.objects.all()
    for user in users:
        registered_emails.append(user.email)
    if request.user.is_anonymous():
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
                    return render_to_response('cfp.html', context)
            else:

                context['form'] = form
                return render_to_response('user-register.html', context)
        else:
            form = UserRegisterForm()
        context['form'] = form
        return render_to_response('user-register.html', context)
    else:
        context['user'] = request.user
        return render_to_response('cfp.html', context)

## View Proposal/Abstract
@login_required
def view_abstracts(request):
    user = request.user
    context = {}
    count_list =[]
    if request.user.is_authenticated:
        if user.is_superuser :
            proposals = Proposal.objects.all().order_by('status')
            ratings = Ratings.objects.all()
            context['ratings'] = ratings
            context['proposals'] = proposals
            context['user'] = user
            return render(request, 'view-proposals.html', context)
        elif user is not None:
            if Proposal.objects.filter(user = user).exists :
                proposals = Proposal.objects.filter(user = user).order_by('status')
                proposal_list= [pro.proposal_type for pro in proposals]
                if 'WORKSHOP' in proposal_list and 'ABSTRACT' in proposal_list:
                    proposal_type = 'BOTH'
                elif 'WORKSHOP' in proposal_list and 'ABSTRACT' not in proposal_list:
                    proposal_type = 'WORKSHOP'
                else:
                    proposal_type = 'ABSTRACT' 

                context['counts'] = count_list
                context['proposals'] =proposals
                context['type'] = proposal_type
                context['user'] = user
            return render(request, 'view-proposals.html', context)
        else:
            return render(request, 'cfp.html')
    else:
        return render(request, 'cfp.html', context)

def cfp(request):
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
            proposals = Proposal.objects.filter(user = request.user).count()
            context['user'] = user
            context['proposals'] = proposals
            return render_to_response('cfp.html', context)
        else:
            context['invalid'] = True
            context['form'] = UserLoginForm
            context['user'] = user
            return render_to_response('cfp.html', context)
    else:
        form = UserLoginForm()
        context = {'request': request,
                    'user': request.user,
                    }
        template = loader.get_template('cfp.html')
        return HttpResponse(template.render(context, request))


@login_required
def submitcfp(request):
    context = {}
    if request.user.is_authenticated:
        social_user = request.user

        django_user = User.objects.get(username=social_user)
        context['user'] = django_user
        proposals_a = Proposal.objects.filter(user = request.user, proposal_type = 'ABSTRACT').count()
        if request.method == 'POST':
            form = ProposalForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                data.user = django_user
                data.email = social_user.email
                data.save()
                context['proposal_submit'] = True
                sender_name = "SciPy India 2017"
                sender_email = TO_EMAIL
                subject = "SciPy India 2017 – Talk Proposal Submission Acknowledgment"
                to = (social_user.email, TO_EMAIL)
                message = """
                Dear {0}, <br><br>
                Thank you for showing interest & submitting a talk proposal at SciPy India 2017 conference for the talk titled <b>“{1}”</b>. Reviewal of the proposals will start once the CFP closes.
                <br><br>You will be notified regarding comments/selection/rejection of your talk via email.
                Visit this {2} link to view status of your submission.
                <br>Thank You ! <br><br>Regards,<br>SciPy India 2017,<br>FOSSEE - IIT Bombay.
                """.format(
                social_user.first_name,
                request.POST.get('title', None),
                'http://scipy.in/2017/view-abstracts/',  )
                email = EmailMultiAlternatives(
                subject,'',
                sender_email, to,
                headers={"Content-type":"text/html;charset=iso-8859-1"}
                )
                email.attach_alternative(message, "text/html")
                email.send(fail_silently=True)
                return render_to_response('cfp.html', context)
            else:
                context['proposal_form'] =  form
                context['proposals_a'] = proposals_a
                template = loader.get_template('submit-cfp.html')
                return HttpResponse(template.render(context, request))
        else:
            form = ProposalForm()
            context['proposals_a'] = proposals_a 
            return render(request, 'submit-cfp.html', {'form': form})
    else:
        context['login_required'] = True
        return render_to_response('cfp.html', context)

