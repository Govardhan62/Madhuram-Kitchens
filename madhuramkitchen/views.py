from django.shortcuts import render, redirect, get_object_or_404
from .forms import CategoryForm, MenuItemForm
from .models import Category, MenuItem, Order, OrderItem,User
from django.contrib import messages
import datetime
from decimal import Decimal
from django.contrib.auth import authenticate, login,get_user_model
from django.contrib.auth.models import User ,auth
from phonenumbers import parse, is_valid_number, NumberParseException
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
User = get_user_model()
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_details.html', {'order': order})

def users_table(request):
    users =User.objects.all()
    return render(request,'users.html',{'users':users})
def orders_table(request):
    orders = Order.objects.all().prefetch_related('items__menu_item')
    return render(request, 'orders_table.html', {'orders': orders})

def back(request):
    return redirect('/')

def logout(request):
    auth.logout(request)
    return redirect('/')

def supervisorlogout(request):
    logout(request)
    return redirect('/')


def supervisor(request):
    if request.method =='POST':
        username =request.POST['username']
        password =request.POST['password']

        user = auth.authenticate(username=username,password=password)
        if  user is not None:
            if user.is_staff:
              auth.login(request,user)
              return redirect ("/")
            else:
              messages.info(request,'You are not authorized  to  access this page.')
              return redirect('supervisor')
        else:
          messages.info(request, 'Invalid Credentials')
          return redirect('supervisor')
    else:
        return render(request,'admin.html')


def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = request.POST['phone_number']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 == password2:
            if User.objects.filter(phone_number=phone_number).exists():
                messages.info(request, 'Phone number is already taken')
                return redirect('signup')
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email is already taken')
                return redirect('signup')
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username is already taken')
                return redirect('signup')
            
            user = User.objects.create_user(
                phone_number=phone_number,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username
            )
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Specify the backend
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')
    
    return render(request, 'signup.html')



def log(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        password = request.POST.get('password')
        otp = request.POST.get('otp')

        # Check if user_input is an email or phone number
        try:
            phone_number = parse(user_input, None)
            if is_valid_number(phone_number):
                user = authenticate(request, phone_number=user_input, otp=otp)
            else:
                user = None
        except NumberParseException:
            user = authenticate(request, email=user_input, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('log')
    
    return render(request, 'login.html')

def index(request):
    categories = Category.objects.all()
    menu_items = MenuItem.objects.all()
    context = {
        'categories': categories,
        'menu_items': menu_items,
    }
    return render(request, 'index.html', context)

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category_name = form.cleaned_data['name']
            if Category.objects.filter(name=category_name).exists():
                messages.error(request, 'Category already exists.')
            else:
                category = form.save()
                if 'add_another_category' in request.POST:
                    return redirect('add_category')
                else:
                    return redirect('add_menu_item', category_id=category.id)
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})

def add_menu_item(request, category_id=None):
    if category_id:
        category = get_object_or_404(Category, id=category_id)
    else:
        category = None

    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            if MenuItem.objects.filter(title=title, category=form.cleaned_data['category']).exists():
                messages.error(request, 'Menu item already exists in this category.')
            else:
                menu_item = form.save(commit=False)
                menu_item.category = form.cleaned_data['category']
                menu_item.save()
                if 'add_another' in request.POST:
                    return redirect('add_menu_item', category_id=menu_item.category.id)
                else:
                    return redirect('menu_items')
    else:
        form = MenuItemForm(initial={'category': category})
    return render(request, 'add_menu_item.html', {'form': form, 'category': category})

def menu_items(request):
    categories = Category.objects.all()
    menu_items = MenuItem.objects.all()
    error_message = None

    if request.method == 'POST':
        selected_items = request.POST.getlist('menu_items')
        quantities = request.POST.getlist('quantities')

        if not selected_items or not any(quantities):
            error_message = "Please select at least one item."
        else:
            order_items = []
            total_price = Decimal('0.00')

            for item_id, quantity in zip(selected_items, quantities):
                if int(quantity) > 0:  # Ensure that the quantity is greater than 0
                    item = MenuItem.objects.get(id=item_id)
                    item_total_price = item.price * Decimal(quantity)
                    total_price += item_total_price
                    order_items.append({
                        'menu_item_id': item.id,
                        'menu_item_title': item.title,
                        'quantity': quantity,
                        'price': float(item_total_price)
                    })

            if order_items:
                # Save order details in session
                request.session['order_items'] = order_items
                request.session['total_price'] = float(total_price)

                # Redirect to order successful page
                return redirect('order_successful')
            else:
                error_message = "Please select at least one item."

    return render(request, 'menu_items.html', {'menu_items': menu_items, 'categories': categories, 'error_message': error_message})


def order_successful(request):
    order_items = request.session.get('order_items')
    total_price = request.session.get('total_price')
    user = request.user

    if not order_items or not total_price:
        return redirect('menu_items')
    

    # Create the order in the database
    order = Order.objects.create(
        user =user,
        total_price=Decimal(total_price),
        created_at=datetime.datetime.now(),
    ) 

    # Create order items
    for item in order_items:
        menu_item = MenuItem.objects.get(id=item['menu_item_id'])
        OrderItem.objects.create(order=order, menu_item=menu_item, quantity=item['quantity'])

    # Clear session data after creating the order
    del request.session['order_items']
    del request.session['total_price']

        # Send order confirmation email
    subject = 'Order Summary'
    html_message = render_to_string('order_successful.html', {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'user': user,
    })
    plain_message = strip_tags(html_message)
    from_email = 'pelurigovardhan@gmail.com'
    to = user.email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)


    return render(request, 'order_successful.html', {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'user':user
    })



# API Views
from rest_framework import viewsets
from .serializers import CategorySerializer, MenuItemSerializer, OrderSerializer, OrderItemSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
