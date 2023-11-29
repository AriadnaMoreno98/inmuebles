from rest_framework.exceptions import ValidationError
from inmuebleslist_app.models import Inmueble, Empresa, Comentario
from inmuebleslist_app.api.serializers import InmuebleSerializer, EmpresaSerializer, ComentarioSerializer
from rest_framework.response import Response
# from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics, mixins
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from inmuebleslist_app.api.permissions import IsAdminOrReadOnly, IsComentarioUserOrReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from inmuebleslist_app.api.throttling import ComentarioCreateThrottle, ComentarioListThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from inmuebleslist_app.api.pagination import InmueblePagination, InmuebleLOPagination

#para filtrar por usuario
class UsuarioComentario(generics.ListAPIView):
    serializer_class = ComentarioSerializer
    
    def get_queryset(self):
        username = self.kwargs['username']
        return Comentario.objects.filter(comentario_user__username=username)
        

class ComentarioCreate(generics.CreateAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ComentarioCreateThrottle]
    
    def get_queryset(self):
        return Comentario.objects.all()
    
    def perform_create(self, serializer):
        pk = self.kwargs['pk']
        inmueble = Inmueble.objects.get(pk=pk)
        
        user = self.request.user
        comentario_queryset = Comentario.objects.filter(inmueble=inmueble, comentario_user=user)
        
        if comentario_queryset.exists():
            raise ValidationError("Ya has comentado sobre este inmueble")
        
        if inmueble.avg_calificacion == 0:
            inmueble.avg_calificacion = serializer.validated_data['calificacion']
        else:
            inmueble.avg_calificacion = (inmueble.avg_calificacion + serializer.validated_data['calificacion']) / 2
            
        inmueble.number_calificacion += 1
        inmueble.save()
        
        serializer.save(inmueble=inmueble, comentario_user=user)

class ComentarioList(generics.ListCreateAPIView):
    # queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    # permission_classes = [IsAuthenticated]
    throttle_classes = [ComentarioListThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['comentario_user__username', 'active']
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Comentario.objects.filter(inmueble=pk)
    
class ComentarioDetail(generics.RetrieveUpdateDestroyAPIView):
    # queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsComentarioUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'comentario-detail'
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Comentario.objects.filter(pk=pk)

# class ComentarioList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#     queryset = Comentario.objects.all()
#     serializer_class = ComentarioSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
    
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
    
# class ComentarioDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#     queryset = Comentario.objects.all()
#     serializer_class = ComentarioSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

class EmpresaVS(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer

# class EmpresaVS(viewsets.ViewSet):
    
#     def list(self, request):
#         queryset = Empresa.objects.all()
#         serializer = EmpresaSerializer(queryset, many=True)
#         return Response(serializer.data)
    
#     def retrieve(self, request, pk=None):
#         queryset = Empresa.objects.all()
#         inmuebleslist = get_object_or_404(queryset, pk=pk)
#         serializer = EmpresaSerializer(inmuebleslist)
#         return Response(serializer.data)
    
#     def create(self, request):
#         deserializer = EmpresaSerializer(data=request.data)
#         if deserializer.is_valid():
#             deserializer.save()
#             return Response(deserializer.data, status=status.HTTP_201_CREATED)
#         return Response(deserializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def update(self, request, pk=None):
#         queryset = Empresa.objects.all()
#         empresa = get_object_or_404(queryset, pk=pk)
#         deserializer = EmpresaSerializer(empresa, data=request.data)
#         if deserializer.is_valid():
#             deserializer.save()
#             return Response(deserializer.data)
#         return Response(deserializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def destroy(self, request, pk):
#         queryset = Empresa.objects.all()
#         empresa = get_object_or_404(queryset, pk=pk)
#         empresa.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class EmpresaAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self, request):
        empresas = Empresa.objects.all()
        serializer = EmpresaSerializer(empresas, many=True, context={'request': request})   
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        deserializer = EmpresaSerializer(data=request.data, context={'request': request})
        if deserializer.is_valid():
            deserializer.save()
            return Response(deserializer.data, status=status.HTTP_201_CREATED)
        return Response(deserializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EmpresaDetalleAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self, request, pk):
        try:
            empresas = Empresa.objects.get(pk=pk)
            serializer = EmpresaSerializer(empresas, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Empresa.DoesNotExist:
            return Response({'Error':'Empresa no existe'}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, pk):
        try: 
            empresas = Empresa.objects.get(pk=pk)
            deserializer = EmpresaSerializer(empresas, data=request.data, context={'request': request})
            if deserializer.is_valid():
                deserializer.save()
                return Response(deserializer.data, status=status.HTTP_200_OK)
            return Response(deserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Empresa.DoesNotExist:
            return Response({'Error':'Empresa no existe'}, status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, pk):
        try:
            empresas = Empresa.objects.get(pk=pk)
            empresas.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Empresa.DoesNotExist:
            return Response({'Error':'Empresa no existe'}, status=status.HTTP_404_NOT_FOUND)

class InmuebleList(generics.ListAPIView):
    queryset = Inmueble.objects.all()
    serializer_class = InmuebleSerializer
    pagination_class = InmueblePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa__nombre', 'direccion']
    search_fields = ['direccion']

class InmuebleListAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self, request):
        inmuebles = Inmueble.objects.all()
        serializer = InmuebleSerializer(inmuebles, many=True)   
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        deserializer = InmuebleSerializer(data=request.data)
        if deserializer.is_valid():
            deserializer.save()
            return Response(deserializer.data, status=status.HTTP_201_CREATED)
        return Response(deserializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class InmuebleDetalleAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self, request, pk):
        try:
            inmuebles = Inmueble.objects.get(pk=pk)
            serializer = InmuebleSerializer(inmuebles)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Inmueble.DoesNotExist:
            return Response({'Error':'Inmueble no existe'}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, pk):
        try: 
            inmuebles = Inmueble.objects.get(pk=pk)
            deserializer = InmuebleSerializer(inmuebles, data=request.data)
            if deserializer.is_valid():
                deserializer.save()
                return Response(deserializer.data, status=status.HTTP_200_OK)
            return Response(deserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Inmueble.DoesNotExist:
            return Response({'Error':'Inmueble no existe'}, status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, pk):
        try:
            inmuebles = Inmueble.objects.get(pk=pk)
            inmuebles.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Inmueble.DoesNotExist:
            return Response({'Error':'Inmueble no existe'}, status=status.HTTP_404_NOT_FOUND)