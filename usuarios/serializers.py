from rest_framework import serializers
from django.contrib.auth.models import User
from usuarios.models import UsuarioProfile
from medicos.models import Medico, IntegracaoAPILog
from empresas.models import Empresa, ConvenioMedico

# ==================== USUARIOS ====================
class UsuarioProfileSerializer(serializers.ModelSerializer):
    nome_completo = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UsuarioProfile
        fields = [
            'id', 'username', 'email', 'nome_completo', 'role', 'status',
            'pode_gerenciar_usuarios', 'pode_gerenciar_medicos',
            'pode_gerenciar_empresas', 'pode_acessar_relatorios',
            'data_criacao', 'data_ultimo_login'
        ]
        read_only_fields = ['id', 'data_criacao', 'data_ultimo_login']


class UsuarioCreateSerializer(serializers.Serializer):
    """Serializer para criar novo usuário"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(min_length=8, write_only=True)
    role = serializers.ChoiceField(choices=['superuser', 'gerencial', 'tatico', 'operacional'])
    status = serializers.ChoiceField(choices=['ativo', 'inativo', 'suspenso'], default='ativo')
    
    def create(self, validated_data):
        role = validated_data.pop('role')
        status = validated_data.pop('status')
        
        user = User.objects.create_user(**validated_data)
        profile = UsuarioProfile.objects.create(
            user=user,
            role=role,
            status=status
        )
        profile.set_permissions_by_role()
        return profile


# ==================== MÉDICOS ====================
class MedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medico
        fields = [
            'id', 'nome', 'email', 'telefone', 'crm', 'especialidade',
            'conselho_regional', 'cpf', 'status', 'is_integrado_cfm',
            'is_integrado_crm', 'data_criacao', 'data_atualizacao',
            'data_ultima_sincronizacao'
        ]
        read_only_fields = [
            'id', 'data_criacao', 'data_atualizacao', 'data_ultima_sincronizacao',
            'is_integrado_cfm', 'is_integrado_crm'
        ]


class IntegracaoAPILogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegracaoAPILog
        fields = [
            'id', 'tipo', 'status', 'quantidade_registros', 'quantidade_sucesso',
            'quantidade_erro', 'mensagem_erro', 'data_inicio', 'data_conclusao'
        ]
        read_only_fields = ['id', 'data_inicio']


# ==================== EMPRESAS ====================
class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = [
            'id', 'razao_social', 'nome_fantasia', 'cnpj', 'email', 'telefone',
            'telefone_secundario', 'endereco', 'cidade', 'estado', 'cep',
            'segmento', 'descricao', 'contato_nome', 'contato_email',
            'contato_telefone', 'status', 'ativo', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['id', 'data_criacao', 'data_atualizacao']


class ConvenioMedicoSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.CharField(source='empresa.razao_social', read_only=True)
    medico_nome = serializers.CharField(source='medico.nome', read_only=True)
    
    class Meta:
        model = ConvenioMedico
        fields = [
            'id', 'empresa', 'empresa_nome', 'medico', 'medico_nome',
            'descricao', 'valor_consulta', 'status', 'data_inicio', 'data_fim',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['id', 'data_criacao', 'data_atualizacao']
