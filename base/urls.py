from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    path('post/<str:pk>/', views.post, name="post"),
    path('browse/<str:tk>/', views.browse, name="browse"),
    path('register/', views.register_user, name="register-user"),
    path('login/', views.login_user, name="login-user"),
    path('logout/', views.logout_user, name="logout-user"),
    path('activate-user/<uidb64>/<token>/', views.activate_user, name='activate'),
    path('reset-password/', views.sendResetPassword, name="send-reset-password"),
    path('password-reset/<uid64>/<token>', views.checkResetToken, name="reset-password"),
    path('create-post/<str:tk>/', views.createPost, name="create-post"),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('settings/', views.userSettings, name='user-settings'),
    path('check/<str:pk>/', views.checkHTMX, name='check-htmx'),
    path('add-comment/<str:pk>/', views.addComment, name='add-comment'),
    path('edit-content/<str:pk>/<str:sk>', views.editContent, name='edit-content'),
    path('add-reaction/<int:pk>/<str:sk>/<int:tk>', views.addReaction, name='add-reaction'),
    path('remove-reaction/<int:id>/<str:type>/', views.removeReaction, name='remove-reaction'),
    path('more-comments/<int:nr>/<int:post_id>', views.moreComments, name='more-comments'),
    path('profile-comments-get/<int:userid>/<int:pagamount>', views.profileComments, name='profile-comments-get'),
    path('profile-posts-get/<int:userid>/<int:pagamount>', views.profilePosts, name='profile-posts-get'),
    path('profile-activity-get/<int:userid>/<int:pagamount>', views.profileActivity, name='profile-activity-get'),
    path('delete-comment/<int:commentid>', views.deleteComment, name='delete-comment'),
    path('lock-post/<int:postid>', views.lockPost, name='lock-post'),
    path('unlock-post/<int:postid>', views.unlockPost, name='unlock-post'),
    path('get-edit-history/<int:id>/<str:type>', views.editHistory, name='edit-history'),
    path('notifications/', views.notifications, name='notifications'),
    path('notification-seen/<int:notificationid>',views.notificationSeen, name='notification-seen'),
    path('delete-post/<int:postid>', views.deletePost, name='delete-post'),
    path('move-thread/<int:post>/<int:topic>', views.moveThread, name='move-thread'),
    path('get-topics/<int:post>/', views.getTopics, name='get-topics'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
