from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuItemViewSet, OrderViewSet, add_category, add_menu_item, menu_items, order_successful, index,log,signup,logout,supervisor,supervisorlogout,orders_table,users_table,back

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'menu_items', MenuItemViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', index, name='index'),
    path('log',log,name='log'),
    path('signup',signup,name='signup'),
    path('logout',logout,name='logout'),
    path('supervisorlogout',supervisorlogout,name='supervisorlogout'),
    path('supervisor',supervisor,name='supervisor'),
    path('orders_table',orders_table,name="orders_table"),
    path('users_table',users_table,name='users_table'),
    path('back',back,name='back'),
    path('add_category/', add_category, name='add_category'),
    path('add_menu_item/<int:category_id>/', add_menu_item, name='add_menu_item'),
    path('menu_items/', menu_items, name='menu_items'),
    path('order_successful/', order_successful, name='order_successful'),  # Updated from place_order
    path('', include(router.urls)),
]
