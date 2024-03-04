from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, OrderForm
from .models import CustomUser, Coin
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal
import json
from datetime import datetime

def LoginView(request):
    if request.method == "GET":
        return render(request, "login.html", {"form":AuthenticationForm()})
    
    else:
        form = AuthenticationForm(data=request.POST)   

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            login(request,user)
            return redirect("dashboard")
            
        return render(request, "login.html", {"form":form})

def RegisterView(request):
    if request.method == "GET":
        return render(request, "register.html",{"form":CustomUserCreationForm()})
    
    else:
        form = CustomUserCreationForm(data=request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.portfolio_value = user.money
            user.portfolio_graph = json.dumps({"date": [str(datetime.now())], "value": [float(user.money)]})
            user.save()
            login(request,user)
            return redirect('dashboard')

    return render(request, "register.html", {"form":form})

def LogoutView(request):
    if request.method == "POST":
        logout(request)
        messages.success(request,"Successfully logged out.")
        return redirect("login")
    
def DashboardView(request):
    if not request.user.is_authenticated:
        messages.error(request,"You do not have permission to access this page.")
        return redirect('login')

    if request.method == "GET":
        # crypto_value for the money overview
        crypto_value = request.user.portfolio_value - request.user.money

        # piechart_data for the piechart
        piechart_data = {"data":[]}

        piechart_data['data'].append({'coin_name':'cash',
                                          'coin_value': str(round(request.user.money,2)), 
                                          'coin_quantity': str(request.user.money),
                                          'share': str(round(request.user.money/request.user.portfolio_value*100,2))})

        for (coin_name, coin_quantity) in request.user.portfolio_dict.items():
            print('coin_name:', coin_name)
            coin = Coin.objects.get(symbol=coin_name)
            coin_value = coin.price * Decimal(coin_quantity)
            piechart_data['data'].append({'coin_name':coin_name,
                                          'coin_price': str(coin.price),
                                          'coin_value': str(round(coin_value,2)), 
                                          'coin_quantity': str(coin_quantity),
                                          'share': str(round(coin_value/request.user.portfolio_value*100,2))})
        
        piechart_data_json = json.dumps(piechart_data)
        
        return render(request, "dashboard.html", {'crypto': crypto_value, 'piechart_data': piechart_data_json})
    
def DataView(request):
    if request.method == "GET":
        coin_symbol = request.GET.get("coin_symbol")
        sort = request.GET.get("sort")
        data = list(Coin.objects.filter(Q(symbol__contains = coin_symbol) | Q(name__contains = coin_symbol)).values())

        if (sort == 'market_cap'):
            data = sorted(data, key=lambda x: x['market_cap'], reverse=True)

        if (sort == 'percent_change_24h_descending'):
            data = sorted(data, key=lambda x: x['percent_change_24h'], reverse=True)

        if (sort == 'percent_change_24h_ascending'):
            data = sorted(data, key=lambda x: x['percent_change_24h'], reverse=False)

        if (sort == 'owned'):
            data = sorted(data, key=lambda x: Decimal(request.user.portfolio_dict.get(x['symbol'],0))*x['price'], reverse=True)

        if (sort == 'atoz'):
            data = sorted(data, key=lambda x: x['name'].upper(), reverse=False)

        if (sort == 'ztoa'):
            data = sorted(data, key=lambda x: x['name'].upper(), reverse=True)

        return JsonResponse({"data":data})

def CoinView(request,pk):
    if not request.user.is_authenticated:
        messages.error(request,"You do not have permission to access this page.")
        return redirect('login')
    
    number_owned = request.user.portfolio_dict.get(pk, 0)

    if request.method == "GET":
        return render(request,"coinpage.html",{"coin":Coin.objects.get(symbol=pk),"form":OrderForm(), "number_owned":number_owned})
    
    if request.method == "POST":
        form = OrderForm(data=request.POST)
        if form.is_valid():
            order_coin = Coin.objects.get(symbol=pk)
            order_price = order_coin.price
            order_quantity = Decimal(request.POST.get("quantity"))
            order_type = request.POST.get("order_type")

            # case where order type is "buy"
            if order_type == "buy":
                cost = order_price * order_quantity
                if cost <= request.user.money:
                    request.user.money -= cost
                    request.user.save()

                    # update the user's portfolio array
                    request.user.portfolio_dict[pk] = str(Decimal(request.user.portfolio_dict.get(pk, 0)) + order_quantity)
                    request.user.save()
                    messages.success(request, f"Successfully purchased {order_quantity} {pk} for ${round(cost,2)}")
                    return redirect("dashboard")
                else:
                    messages.error(request,"Order unsuccesssful (insufficient funds).")
                    return render(request,"coinpage.html",{"coin":Coin.objects.get(symbol=pk),"form":form,"number_owned":number_owned})
                
            if order_type == "sell":
                owned_quantity = Decimal(request.user.portfolio_dict.get(pk, 0))
                if order_quantity <= owned_quantity:
                    request.user.portfolio_dict[pk] = str(Decimal(request.user.portfolio_dict.get(pk, 0)) - order_quantity)
                    request.user.money += order_quantity * order_price
                    request.user.save()
                    messages.success(request,f"Successfully sold {order_quantity} {order_coin.name} for {order_quantity * order_price}.")
                    return redirect("dashboard")
                else:
                     messages.error(request,"Order unsuccesssful (you don't own enough of this coin).")
                     return render(request,"coinpage.html",{"coin":Coin.objects.get(symbol=pk),"form":form,"number_owned":number_owned})