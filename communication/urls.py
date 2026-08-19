from django.urls import path
from .views import contact_detail_view, contact_messages_list_view,create_contact_view, article_detail_view,article_list_view

app_name = 'communication'
urlpatterns = [
    path('contact-create/',create_contact_view,name='create_contact'),
    path('contact-messages-list/', contact_messages_list_view, name='contact_messages_list'),
    path('conversation/<int:contact_message_id>/', contact_detail_view, name='contact_detail'),
    path('articles/',article_list_view,name='article_list'),
    path('articles/article/<slug:slug>/',article_detail_view, name='article_detail'),

]