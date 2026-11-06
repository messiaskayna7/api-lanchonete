Sistema de lanchonete
Nome: Messias Kaynã Ferreira de Souza

URL: http://127.0.0.1:8000/admin/
Usuário: admin
Senha: admin123

Tecnologias:
Python é a linguagem de programação usada em todo o projeto.

Django é o framework web que cuida do banco, das rotas e do painel admin.

DRF (Django REST Framework) é a extensão do Django que facilita criar APIs REST, com serializers, ViewSets e autenticação.

drf-spectacular gera automaticamente a documentação da API no Swagger.

REST é um jeito de montar APIs em que cada coisa (produto, categoria) tem uma URL, e o método HTTP diz o que fazer com ela. Cada requisição é independente, por isso o token vai sempre junto.

GET busca dados.
POST cria.
PUT substitui o registro inteiro.
PATCH altera só alguns campos.
DELETE apaga.

Como rodar o projeto:

venv\Scripts\activate
python manage.py runserver

Depois abra http://127.0.0.1:8000/admin/ no navegador e entre com admin / admin123.

Para quem baixar o projeto do GitHub pela primeira vez, a sequência completa é esta:

git clone <url-do-repositorio>
cd Lanchonete
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata cardapio.json
python manage.py createsuperuser
python manage.py runserver

RESUMO GERAL:
O Admin (/admin/), cadastra as coisas no navegador, a API(/api/), um site ou app pede os dados e recebe em JSON.

1. settings.py: configuração geral

INSTALLED_APPS lista os componentes ativos: rest_framework (API), rest_framework.authtoken (tokens), drf_spectacular (Swagger) e cardapio (app próprio). O bloco REST_FRAMEWORK define três regras para toda a API. Com IsAuthenticatedOrReadOnly, a leitura fica liberada para todos, mas criar, editar e excluir exigem login. Com TokenAuthentication, o app se identifica enviando Authorization: Token abc123... no cabeçalho. Com a paginação de 5 itens, as listas chegam divididas em páginas, com count, next, previous e results.

2. models.py: estrutura do banco

Cada classe vira uma tabela. Categoria tem nome (sem repetição) e descricao (opcional). Produto tem nome, preco, disponivel e categoria. O campo categoria é um ForeignKey, então cada produto pertence a uma categoria e uma categoria reúne vários produtos. Com related_name='produtos', é possível acessar categoria.produtos.all(). O on_delete=PROTECT bloqueia a exclusão de categorias que ainda têm produtos. As alternativas seriam CASCADE, que excluiria os produtos junto, e SET_NULL, que os deixaria sem categoria. AreaEntrega guarda as cidades atendidas pela lanchonete (extra C5). O **str** define como o objeto aparece em texto, por exemplo no admin.

Nas migrações, o makemigrations compara os models com o banco e gera um plano de alterações em cardapio/migrations/. Depois, o migrate aplica esse plano e cria as tabelas.

3. serializers.py: conversão de dados

Transforma objetos do banco em JSON (num GET) e JSON em objetos validados (num POST). O ModelSerializer gera os campos a partir do model. categoria_nome é um campo extra, só de leitura, que mostra o nome da categoria. O validate_preco roda sozinho e devolve 400 se o preço for negativo. O campo preco foi declarado manualmente para que essa validação tenha prioridade sobre a regra do model.

4. views.py: comportamento da API

O ModelViewSet já oferece todas as operações (listar, detalhar, criar, atualizar total ou parcialmente e excluir) só com queryset e serializer_class. Também foram adicionados o filtro ?disponivel=true via get_queryset, a busca por nome com ?search=, a rota /api/categorias/1/produtos/ com @action(detail=True), um destroy personalizado que troca o erro 500 por 400 com mensagem quando o PROTECT impede a exclusão, e a MunicipiosView, que consulta o IBGE.

5. urls.py: rotas

O DefaultRouter cria as URLs de cada ViewSet e a página índice /api/. A rota municipios/ foi registrada manualmente, porque não usa router. O arquivo principal reúne admin, API, token e Swagger.

6. admin.py: painel administrativo

Define as colunas da lista, os filtros, a busca e a edição rápida de "disponível". Também mostra os produtos dentro da categoria (inline), oferece a ação "Marcar como indisponível" e personaliza o título do painel.

7. ibge.py: consumo de API externa

A rota /api/municipios/?uf=PE valida a UF e responde 400 se ela for inválida, já que o erro é do cliente. Em seguida consulta o IBGE com timeout de 10 segundos, para não ficar presa caso o serviço trave. Se o IBGE falhar, a resposta é 503, porque a falha é externa. Se der certo, a API devolve só o código e o nome de cada município, mais o total. No cadastro de AreaEntrega, o código do município é conferido no IBGE e recusado se não existir, tanto na API quanto no admin.

8. Arquivos auxiliares

O cardapio.json traz dados de exemplo, carregados com loaddata. O requirements.txt lista as dependências, instaladas com pip install -r. O .gitignore deixa de fora o venv/, que é pesado e diferente em cada máquina, e o db.sqlite3, que pode conter dados sensíveis.

Fluxo de exemplo: marcar um produto como indisponível

O app envia PATCH /api/produtos/5/ com {"disponivel": false} e o token. A rota leva a requisição ao partial_update. Sem token válido, a resposta é 401. Com token, o serializer valida os dados e o .save() grava no banco. Por fim, a API devolve 200 com o produto atualizado em JSON.
