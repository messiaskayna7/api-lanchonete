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

Model é a classe que define uma tabela do banco e seus campos, como Produto com nome, preco e categoria.

Serializer é o tradutor entre o model e o JSON: converte os objetos para enviar na resposta e valida os dados que chegam.

ViewSet é a classe que reúne as ações de um recurso (listar, detalhar, criar, editar e apagar) e decide o que fazer em cada requisição.

Router gera automaticamente as URLs de cada ViewSet, como /api/produtos/ e /api/produtos/{id}/.

Juntos, o fluxo fica assim: o router recebe a URL, o viewset executa a ação, o serializer converte os dados e o model acessa o banco.

IBGE:
https://servicodados.ibge.gov.br/api/v1/localidades/estados/{UF}/municipios — lista os municípios de um estado; é usado pelo /api/municipios/.

https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo} — busca um município pelo código; é usado na validação do cadastro de AreaEntrega. Se a resposta vier vazia, o código não existe e o cadastro é recusado.

Endpoints:

Painel e documentação:
/admin/ — painel administrativo
/api/ — página índice com links para todas as rotas
/api/docs/ — documentação Swagger
/api/token/ — gera o token de autenticação (POST com usuário e senha)

Categorias:
GET e POST em /api/categorias/
GET, PUT, PATCH e DELETE em /api/categorias/{id}/
GET em /api/categorias/{id}/produtos/ — produtos de uma categoria (rota extra da @action)

Produtos:
GET e POST em /api/produtos/ (aceita ?disponivel=true, ?search=nome e ?page=2)
GET, PUT, PATCH e DELETE em /api/produtos/{id}/

Áreas de entrega:
GET e POST na rota de lista, e GET, PUT, PATCH e DELETE na rota de detalhe com {id}. O prefixo exato (por exemplo, /api/areas-entrega/) é o que você registrou no router; confira no urls.py.

Municípios (IBGE):
GET em /api/municipios/?uf=PE

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

Respostas:

1. API é um conjunto de regras que permite que um sistema converse com outro, pedindo e enviando dados. Para a lanchonete, ela deixa o cardápio disponível para um site, um app ou um totem, todos usando os mesmos dados cadastrados num só lugar.

2. REST é um estilo de arquitetura para APIs. Características: cada recurso tem sua URL (/api/produtos/), as ações usam os métodos HTTP (GET, POST etc.), cada requisição é independente (sem estado guardado no servidor) e os dados trafegam em formato padrão, geralmente JSON.

3. O Django é o framework web: cuida do banco, das rotas e do admin. O DRF é uma extensão que facilita criar APIs REST, com serializers, ViewSets, autenticação e paginação. Usamos os dois juntos porque o Django dá a base e o DRF transforma essa base numa API.

4. O venv é um ambiente isolado com suas próprias bibliotecas. Usamos um por projeto para evitar conflito de versões entre projetos e para saber exatamente o que cada um precisa.

5. Model é uma classe Python que representa uma tabela do banco. O makemigrations compara os models com o banco e gera um arquivo com as alterações necessárias. O migrate aplica essas alterações e cria ou modifica as tabelas.

6. O ForeignKey liga cada produto a uma categoria, e uma categoria pode ter vários produtos. O related_name='produtos' permite acessar os produtos a partir da categoria com categoria.produtos.all().

7. Escolhi PROTECT. Se a categoria tiver produtos, a exclusão é bloqueada, e a API responde 400 com uma mensagem. Os produtos continuam intactos.

8. Serializer converte objetos Python em JSON e JSON em objetos, validando os dados. A API precisa dele porque o banco trabalha com objetos e a internet com JSON.

9. Serializar é objeto → JSON: um GET em /api/produtos/1/ devolve {"id": 1, "nome": "X-Burguer", ...}. Desserializar é JSON → objeto, com validação: um POST com {"nome": "Pastel", "preco": "8.00", "categoria": 1} é conferido e salvo no banco.

10. JSON é um formato de texto para organizar dados em pares chave/valor. É o mais usado porque é leve, fácil de ler e funciona em praticamente qualquer linguagem.

11. ViewSet é uma classe que agrupa todas as ações de um recurso. O ModelViewSet entrega prontas list, retrieve, create, update, partial_update e destroy.

12. O Router gera as URLs automaticamente a partir dos ViewSets. No projeto: /api/, /api/categorias/, /api/categorias/{id}/, /api/categorias/{id}/produtos/ (pela @action), /api/produtos/, /api/produtos/{id}/, e as rotas de áreas de entrega, lista e detalhe (confira o nome exato no seu urls.py). A rota /api/municipios/ foi registrada manualmente.

13. GET busca dados, POST cria, PUT substitui o registro inteiro, PATCH altera só alguns campos e DELETE apaga. Para marcar um produto como indisponível, eu usaria PATCH, porque só o campo disponivel muda e não é preciso reenviar o produto todo.

14. 200 (OK): um GET na lista ou um PATCH bem-sucedido. 201 (criado): um POST que cadastra um produto. 204 (sem conteúdo): um DELETE que apaga um produto. 400 (requisição inválida): preço negativo, UF inválida ou exclusão bloqueada pelo PROTECT. 404 (não encontrado): um GET em /api/produtos/999/, que não existe.

15. No serializer, no método validate_preco. Se alguém enviar preço negativo, a API devolve 400 com a mensagem de erro do campo preco.

16. O admin é um painel visual no navegador para gerenciar os dados. A API entrega os dados em JSON para outros sistemas. Na lanchonete, o dono ou o funcionário usaria o admin para cadastrar o cardápio, e o site ou o app dos clientes usaria a API.

17. Sim, porque o admin e a API leem e gravam no mesmo banco de dados.

18. list_display define as colunas da lista, list_filter cria os filtros na lateral e search_fields ativa a caixa de busca.

19. O venv é pesado e cada máquina cria o seu. O db.sqlite3 é o banco local e pode ter dados pessoais ou de teste. O requirements.txt lista as bibliotecas do projeto, para instalar tudo com pip install -r requirements.txt.

20. O app faria requisições HTTP para a API. Por exemplo, para mostrar o cardápio: o app envia GET /api/produtos/?disponivel=true, o urls.py encaminha para o ProdutoViewSet, a view filtra os produtos no banco, o serializer converte o resultado em JSON e a API responde 200 com a lista. O app recebe o JSON e monta a tela. Para ações que alteram dados, como um pedido, o app enviaria também o token no cabeçalho.
