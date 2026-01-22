# AME Caraguatatuba - Sistema de Gestão (Fase 2: Django Backend)

## 📋 Arquitetura do Projeto

```
ame_project/
├── ame_project/          # Settings Django
│   ├── settings.py       # Configurações
│   ├── urls.py          # URLs raiz
│   └── wsgi.py          # WSGI
├── usuarios/            # App de Usuários
│   ├── models.py        # UsuarioProfile
│   ├── views.py         # ViewSets
│   ├── serializers.py   # Serializers
│   └── urls.py          # Rotas
├── medicos/             # App de Médicos
│   ├── models.py        # Medico, IntegracaoAPILog
│   ├── views.py         # ViewSets
│   └── services.py      # Integração com CFM/CRM
├── empresas/            # App de Empresas
│   ├── models.py        # Empresa, ConvenioMedico
│   ├── views.py         # ViewSets
│   └── urls.py          # Rotas
├── api/                 # App de API
│   ├── urls.py          # Router DRF
│   └── permissions.py   # Permissões customizadas
├── templates/           # Templates HTML
├── static/              # CSS, JS, imgs
├── manage.py            # Django CLI
├── requirements.txt     # Dependências
├── .env.example         # Variáveis de ambiente
└── Dockerfile          # Container Docker
```

## 🚀 Quick Start (Desenvolvimento)

### Pré-requisitos
- Python 3.10+
- PostgreSQL 12+
- pip/virtualenv

### 1. Clonar e Configurar

```bash
# Clonar repositório
git clone <seu-repo>
cd ame_project

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Copiar .env.example para .env e configurar
cp .env.example .env
```

### 2. Configurar Banco de Dados

```bash
# Criar usuário PostgreSQL
createuser -P ame_user  # senha: ame_password
createdb -O ame_user ame_db

# Aplicar migrações
python manage.py makemigrations
python manage.py migrate

# Criar superuser
python manage.py createsuperuser
```

### 3. Executar Servidor

```bash
python manage.py runserver
```

Acesse:
- **Django Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/
- **Frontend**: http://localhost:8000/

## 🐳 Deploy com Docker

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar projeto
COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["gunicorn", "ame_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ame_user
      POSTGRES_PASSWORD: ame_password
      POSTGRES_DB: ame_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - SECRET_KEY=your-secret-key
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=ame_db
      - DB_USER=ame_user
      - DB_PASSWORD=ame_password
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      - db

volumes:
  postgres_data:
```

### Executar com Docker

```bash
docker-compose up --build
```

## 📡 Endpoints da API

### Autenticação
```
POST   /api-token-auth/        # Obter token
GET    /api/users/me/          # Dados do usuário
POST   /api/users/logout/      # Logout
```

### Usuários
```
GET    /api/usuarios/           # Listar usuários
POST   /api/usuarios/           # Criar usuário
GET    /api/usuarios/{id}/      # Detalhes
PUT    /api/usuarios/{id}/      # Atualizar
DELETE /api/usuarios/{id}/      # Deletar
```

### Médicos
```
GET    /api/medicos/            # Listar médicos
POST   /api/medicos/            # Criar médico
GET    /api/medicos/{id}/       # Detalhes
PUT    /api/medicos/{id}/       # Atualizar
DELETE /api/medicos/{id}/       # Deletar
POST   /api/medicos/import/     # Importar (CSV, CFM, CRM)
GET    /api/medicos/logs/       # Histórico de integrações
```

### Empresas
```
GET    /api/empresas/           # Listar empresas
POST   /api/empresas/           # Criar empresa
GET    /api/empresas/{id}/      # Detalhes
PUT    /api/empresas/{id}/      # Atualizar
DELETE /api/empresas/{id}/      # Deletar
GET    /api/convenios/          # Listar convênios
```

## 🔐 Sistema de Permissões

### Níveis de Acesso
1. **Superuser** - Acesso total a todos os módulos
2. **Gerencial** - Gerencia usuários, médicos, empresas e relatórios
3. **Tático** - Gerencia médicos e acessa relatórios
4. **Operacional** - Apenas consulta (read-only)

### Implementação (middleware)

```python
# api/permissions.py
from rest_framework.permissions import BasePermission

class CanGerenciarUsuarios(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.pode_gerenciar_usuarios

class CanGerenciarMedicos(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.pode_gerenciar_medicos
```

## 🔄 Integração com APIs Externas

### CFM Brasil

```python
# medicos/services.py
import requests

class CFMIntegracaoService:
    BASE_URL = "https://api.cfm.org.br/v1"  # Exemplo (usar URL real)
    
    @staticmethod
    def verificar_crm(crm, uf):
        """Verifica validade do CRM no CFM"""
        response = requests.get(
            f"{CFMIntegracaoService.BASE_URL}/medicos/{crm}",
            params={'uf': uf},
            headers={'Authorization': f'Bearer {settings.CFM_API_KEY}'}
        )
        return response.json()
    
    @staticmethod
    def importar_dados_medicos():
        """Importa dados de médicos da API CFM"""
        # Implementação de importação em batch
        pass
```

### Upload CSV

```python
# medicos/views.py
from rest_framework.decorators import action
from rest_framework.response import Response
import csv

class MedicoViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        file = request.FILES['file']
        reader = csv.DictReader(file)
        
        for row in reader:
            Medico.objects.create(
                nome=row['nome'],
                crm=row['crm'],
                # ... outros campos
            )
        
        return Response({'status': 'success', 'imported': len(list(reader))})
```

## 📊 Relatórios e Analytics

```python
# medicos/views.py
@action(detail=False, methods=['get'])
def relatorio_medicos_por_especialidade(self, request):
    from django.db.models import Count
    
    relatorio = Medico.objects.values('especialidade').annotate(
        total=Count('id')
    ).order_by('especialidade')
    
    return Response(relatorio)
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com coverage
pytest --cov=usuarios --cov=medicos --cov=empresas

# Teste específico
pytest usuarios/tests/test_models.py::TestUsuarioProfile
```

## 📚 Estrutura de Pastas por App

```
usuarios/
├── migrations/
├── __init__.py
├── admin.py          # Configuração do admin
├── apps.py
├── models.py         # UsuarioProfile
├── serializers.py    # UsuarioProfileSerializer
├── views.py          # UsuarioViewSet
├── permissions.py    # Permissões
├── tests.py
└── urls.py

medicos/
├── migrations/
├── __init__.py
├── admin.py
├── apps.py
├── models.py         # Medico, IntegracaoAPILog
├── serializers.py    # MedicoSerializer
├── views.py          # MedicoViewSet com import/export
├── services.py       # Integração CFM, CRM, CSV
├── permissions.py
├── tests.py
└── urls.py

empresas/
├── migrations/
├── __init__.py
├── admin.py
├── apps.py
├── models.py         # Empresa, ConvenioMedico
├── serializers.py
├── views.py
├── tests.py
└── urls.py
```

## 🎯 Próximas Etapas

1. **Autenticação JWT** - Implementar JWT para SPA
2. **Notifications** - Sistema de notificações com Celery
3. **Analytics Dashboard** - Gráficos em tempo real
4. **Mobile API** - Endpoint otimizado para mobile
5. **Integração Real** - Conectar com APIs reais de CFM/CRM
6. **CI/CD** - GitHub Actions para deploy automático

## 📞 Suporte

Para dúvidas sobre a estrutura ou integração, consulte:
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Docs](https://docs.djangoproject.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
