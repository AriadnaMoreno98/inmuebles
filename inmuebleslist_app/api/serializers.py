from rest_framework import serializers
from inmuebleslist_app.models import Inmueble, Empresa, Comentario

class ComentarioSerializer(serializers.ModelSerializer):
    comentario_user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Comentario
        # fields = '__all__'
        exclude = ['inmueble']

class InmuebleSerializer(serializers.ModelSerializer):
    
    comentarios = ComentarioSerializer(many=True, read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.nombre')
        
    class Meta:
        model = Inmueble
        fields = '__all__'
        # fields = ('descripcion', 'direccion', 'pais', 'imagen')
        # exclude = ('active', 'id')

class EmpresaSerializer(serializers.ModelSerializer):
    
    inmuebleslist = InmuebleSerializer(many = True, read_only=True)
    # inmuebleslist = serializers.StringRelatedField(many=True)
    # inmuebleslist = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # inmuebleslist = serializers.HyperlinkedIdentityField(many=True, read_only=True, view_name='inmueble-detalle')
    
    class Meta:
        model = Empresa
        fields = '__all__'
        # fields = ('nombre', 'website')
        # exclude = ('active', 'id')