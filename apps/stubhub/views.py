# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponse

from models import User, Ticket, Event, Performer, Venue, Category

from django.contrib import messages

import re

import bcrypt


#-----------------------------------------------------------------
#-----------------------------------------------------------------


def index(request):
    
    all_events = Event.objects.order_by('event_date_time', 'popularity_score')
    categories = Category.objects.order_by('tag')
    context = {
        'selected_events': all_events,
        'categories': categories
    }

  
    return render(request, 'stubhub/home.html', context)


#-----------------------------------------------------------------
#-----------------------------------------------------------------

def register(request):
    
    errors = User.objects.new_user_validator(request.POST)
    if len(errors):
        for tag, error in errors.iteritems():
            messages.add_message(request, messages.ERROR, errors[tag])
        return redirect("/log_reg")
    else:
        first =  request.POST['first_name']
        last =  request.POST['last_name']
        mail = request.POST['email']
        hash1 = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
 
        user = User.objects.create(first_name=first, last_name=last, email=mail, password_hash=hash1)

        if not user:
            messages.add_message(request, messages.ERROR, "User email already exists.")
            return redirect("/")
        else:
            request.session['user_id'] = user.id
            return redirect('/success')

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def success(request):
    
    user = User.objects.get(id=request.session['user_id'])

    all_events = Event.objects.order_by('event_date_time', 'popularity_score')
    categories = Category.objects.order_by('tag')

    context = { 
        'user': User.objects.get(id=request.session['user_id']),
        'selected_events': all_events,
        'categories': categories
    }
    
    return render(request, 'stubhub/home.html', context)
    

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def login(request):
    errors = User.objects.login_validator(request.POST)
    email = request.POST['email']
    if len(errors):
        messages.add_message(request, messages.ERROR, "Invalid email or password.")
        return redirect("/log_reg")
    else:
        user = User.objects.get(email=email)
        request.session['user_id'] = user.id
        return redirect ('/success')

#-----------------------------------------------------------------
#----------------------------------------------------------------

def log_out(request):
    for sesskey in request.session.keys():
        del request.session[sesskey]
    return redirect("/")

#-----------------------------------------------------------------
#-----------------------------------------------------------------


def init_sale(request, parameter):
    
    event_id = parameter
    event = Event.objects.get(id=event_id)

    context = {
        "event": event,
    }

    return render(request, 'stubhub/init_sale.html', context)


#-----------------------------------------------------------------
#-----------------------------------------------------------------


def post_tickets(request, parameter):
    
    event_id = parameter
    event = Event.objects.get(id=event_id)

    seller_id = request.session['user_id']
    seller = User.objects.get(id=seller_id)

    seat = request.POST['seat']
    price = request.POST['price']

    new_ticket = Ticket.objects.create(event=event, seller=seller, seat=seat, price=price)

    url = '/ticket_posted/'
    url += str(parameter)

    print"-"*50
    print url
    print"-"*50

    return redirect(url)


#-----------------------------------------------------------------
#-----------------------------------------------------------------


def ticket_posted(request, parameter):
    
    event_id = parameter
    event = Event.objects.get(id=event_id)
    
    context = {
        "event": event,
    }

    print"-"*50
    print parameter, context
    print"-"*50

    return render(request, 'stubhub/sell_success.html', context)
    



#-----------------------------------------------------------------
#-----------------------------------------------------------------

def log_reg(request):
    return render (request,"stubhub/login.html")

def acc_info(request):
    context = { 'user': User.objects.get(id=request.session['user_id']),
                'bought_tickets': Ticket.objects.filter(buyer_id=request.session['user_id'])
    }
    
    return render (request,"stubhub/acc_info.html",context)

def sell_tickets(request):
    context = { 'user': User.objects.get(id=request.session['user_id'])
    }

    return render (request,"stubhub/sell_tickets.html",context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def search_results(request):
    search_field = request.session['search_field']
    search_info = request.session['search_info']
    if search_field == 'name':
        selected_events = Events.objects.filter(name__contains=search_info)
    elif search_field == 'venue':
        selected_events = Event.objects.filter(venue__name__contains=search_info)
    elif search_field == 'performer':
        selected_events = Event.objects.filter(performer__name__contains=search_info)
    elif search_field == 'category':
        selected_events = Event.objects.filter(category__tag=search_info)
    elif search_field == 'date':
            selected_events = Event.objects.filter(event_date_time__contains=search_info)    
    num_results = len(selected_events)
    categories = Category.objects.order_by('tag')
    context = {
        'num_results' : num_results,
        'selected_events': selected_events,
        'query': search_info,
        'categories': categories
    }
    return render(request, 'stubhub/search_results.html', context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def process_search(request):
    if request.method == 'POST':
        if len(request.POST['text_search'])>0:
            search_info=request.POST['text_search']
            try:
                Event.objects.filter(name__contains=search_info)
                request.session['search_field']= 'name'
            except:
                try:
                    Venue.objects.filter(name__contains=search_info)
                    request.session['search_field']= 'venue'
                except:
                    try:
                        Perfomer.objects.filter(name__contains=search_info)
                        request.session['search_field']= 'performer'
                    except:
                        selected_events = []
        elif len(request.POST['event_date'])>0:
            search_info = request.POST['event_date']
            request.session['search_field']= 'date'
        elif len(request.POST['category'])>0:
            search_info = request.POST['category']
            request.session['search_field'] = 'category'
        else:
            return redirect('/')
        request.session['search_info'] = search_info
        return redirect('/search')
    else:
        return redirect('/')