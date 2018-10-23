from django.urls import path
from snippets import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.schemas import get_schema_view

# 基于函数的path路径
# urlpatterns = [
#     path('snippets/', views.snippet_list),
#     path('snippets/<int:pk>/', views.snippet_detail)
# ]

schema_view = get_schema_view(title='Pastebin API')

# 基于类的path的路径
urlpatterns = [
    path('snippets/', views.SnippetList.as_view(), name='snippet-list'),
    path('snippets/<int:pk>/', views.SnippetDetail.as_view(), name='snippet-detail'),
    path('users', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('', views.api_root),
    path('snippets/<int:pk>/highlight/', views.SnippetHighlight.as_view(), name='snippet-highlight'),
    path('schema/', schema_view),
]

urlpatterns = format_suffix_patterns(urlpatterns)   # 为了利用我们的响应不再硬连接到单个内容类型这一事实，我们将API格式后缀添加到API端点。使用格式后缀为我们提供了明确引用给定格式的URL，这意味着我们的API将能够处理诸如http://example.com/api/items/4.json之类的 URL