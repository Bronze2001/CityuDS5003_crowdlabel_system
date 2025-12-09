from django.urls import path
from . import views

# API routes
urlpatterns = [
    # auth
    path('auth/login/', views.login_view),
    path('auth/logout/', views.logout_view),
    path('auth/check/', views.check_auth),
    
    # tasks
    path('tasks/next/', views.get_available_task),
    path('tasks/add/', views.add_task),
    path('tasks/active/', views.get_all_active_tasks),
    
    # annotator
    path('annotate/', views.submit_annotation),
    path('stats/', views.get_user_stats),
    path('history/', views.get_user_history),
    
    # admin
    path('admin/reviews/', views.get_review_queue),
    path('admin/resolve/', views.resolve_conflict),
    path('admin/unpaid/', views.get_unpaid_users),
    path('admin/payroll/', views.run_payroll),
]