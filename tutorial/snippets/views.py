from django.shortcuts import render

# Create your views here.

# # from django.http import HttpResponse, JsonResponse
# # from django.views.decorators.csrf import csrf_exempt
# # from rest_framework.renderers import JSONRenderer   # 序列化
# # from rest_framework.parsers import JSONParser   # 反序列化
#
# # 使用Response以及装饰器@api_view来修改视图函数
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from snippets.models import Snippet
# from snippets.serializers import SnippetSerializer
#
#
# @api_view(['GET', 'POST'])
# def snippet_list(request, format=None):
#     """
#     List all code snippets, or create a new snippet
#     """
#     if request.method == 'GET':
#         snippets = Snippet.objects.all()    # 获取所有表元素
#         serializer = SnippetSerializer(snippets, many=True)
#         # return JsonResponse(serializer.data, safe=False)    # 将数据渲染到json
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         # data = JSONParser().parse()     # 将流解析为Python本机数据类型
#         # serializer = SnippetSerializer(data=data)
#         serializer = SnippetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             # return JsonResponse(serializer.data, status=201)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         # return JsonResponse(serializer.errors, status=400)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def snippet_detail(request, pk, format=None):
#     """
#     Retrieve, update or delete a code snippet.
#     """
#     try:
#         snippet = Snippet.objects.get(pk=pk)
#     except Snippet.DoesNotExist:
#         # return HttpResponse(status=400)
#         return Response(status=status.HTTP_400_BAD_REQUEST)
#
#     if request.method == 'GET':
#         serializer = SnippetSerializer(snippet)
#         # return JsonResponse(serializer.data)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         # data = JSONParser().parse(request)
#         # serializer = SnippetSerializer(snippet, data=data)
#         serializer = SnippetSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             # return JsonResponse(serializer.data)
#             return Response(serializer.data)
#         # return JsonResponse(serializer.errors, status=400)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         snippet.delete()
#         # return HttpResponse(status=204)
#         return Response(status=status.HTTP_204_NO_CONTENT)


# from snippets.models import Snippet
# from snippets.serializers import SnippetSerializer
# from django.http import Http404
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
#
#
# class SnippetList(APIView):
#     """
#     List all snippets, or create a new snippet.
#     """
#     def get(self, request, format=None):
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = SnippetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class SnippetDetail(APIView):
#     """
#     Retrieve, update or delete a snippet instance.
#     """
#     def get_object(self, pk):
#         try:
#             return Snippet.objects.get(pk=pk)
#         except Snippet.DoesNotExist:
#             return Http404
#
#     def get(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet)
#         return Response(serializer.data)
#
#     def put(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# 使用基于类的通用函数
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from rest_framework import generics
from snippets.permissions import IsOwnerOrReadOnly
from rest_framework import permissions


class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    # 户不是作为序列化表示的一部分发送的，而是传入请求的属性。
    # 我们处理的方式是通过覆盖.perform_create()我们的代码段视图上的方法，允许我们修改实例保存的管理方式，并处理传入请求或请求的URL中隐含的任何信息。
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

# 因为在User模型上'snippets'是反向关系，所以在使用ModelSerializer类时默认情况下不会包含它，因此我们需要为它添加显式字段。
# 我们还会添加几个视图views.py。我们希望只使用只读视图为用户表示，所以我们将使用ListAPIView和RetrieveAPIView通用的基于类的意见。
from django.contrib.auth.models import User
from snippets.serializers import UserSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'snippets': reverse('snippet-list', request=request, format=format)
    })

from rest_framework import renderers
from rest_framework.response import Response


class SnippetHighlight(generics.GenericAPIView):
    queryset = Snippet.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)