from django.urls import path
from . import views
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('user_login')


urlpatterns = [
	path('', views.home, name="home"),
	path('login/',views.user_login,name='user_login'),
	path('logout/', logout_view, name='logout'),
	path('register/',views.register_owner,name='register_owner'),
	path('owner/', views.owner_dashboard, name='owner_dashboard'),
    path('account',views.account,name='account'),
    path('edit_account',views.edit_account,name='edit_account'),
    path('change-password/', views.change_password, name='change_password'),
	path('weaver/', views.weaver_dashboard, name='weaver_dashboard'),
    path('warper/', views.warper_dashboard, name='warper_dashboard'),
	path('staff_management/',views.staff_management,name='staff_management'),
	path('make_warp/', views.make_warp, name="make_warp"),
    path('warp_list/',views.warp_list,name='warp_list'),
    path('warp_list_warper/', views.warp_list_warper, name='warp_list_warper'),
    path('add_new_warp_design/',views.add_new_warp_design, name='add_new_warp_design'),
    path('edit_warp_design/<int:warp_id>/', views.edit_warp_design, name='edit_warp_design'),
    path('warp_design_list/',views.warp_design_list,name='warp_design_list'),
	path('add_piece/', views.add_piece, name="add_piece"),
	path('date_wise/', views.date_wise, name="date_wise"),
	path('warp_wise/', views.warp_wise, name="warp_wise"),
	path('edit_warp/<int:warp_id>/',views.edit_warp,name="edit_warp"),
	path('edit_wage/<int:warp_id>/', views.edit_wage, name='edit_wage'),
	path('edit_piece/<int:piece_id>/',views.edit_piece,name="edit_piece"),
	path('add_wage/', views.add_wage, name="add_wage"),
	path('transactions/', views.transactions, name="transactions"),
	path('change_wage/<int:id>/', views.change_wage, name="change_wage"),
    path('get-transaction-details/', views.get_transaction_details, name='get_transaction_details'),
    path('warp_management/', views.warp_management, name='warp_management'),
    path('yarn_management/', views.yarn_management, name='yarn_management'),
    path('piece_management/',views.piece_management,name='piece_management'),
	path('create_yarn/', views.create_yarn, name='create_yarn'),
    path('give_yarn/', views.give_yarn, name='give_yarn'),
	path('edit_yarn/<int:yarn_id>/', views.edit_yarn, name='edit_yarn'),
    path('yarn_list/',views.yarn_list,name='yarn_list'),
    path('warp_wise_yarn_list/', views.warp_wise_yarn_list, name='warp_wise_yarn_list'),
    path('make_secondary/<int:warp_id>/', views.make_secondary, name='make_secondary'),
	path('warps/', views.warp_list, name='warp_list'),
    path('warps/<int:warp_id>/complete-warping/', views.complete_warping, name='complete_warping'),
    path('warps/<int:warp_id>/complete-weaving/', views.complete_weaving, name='complete_weaving'),
    path('assign_weaver/<int:warp_id>/',views.assign_weaver,name='assign_weaver')
]