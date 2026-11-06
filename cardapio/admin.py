from django import forms
from django.contrib import admin

from .ibge import IBGEIndisponivel, municipio_existe
from .models import AreaEntrega, Categoria, Produto

# Textos do topo do painel (/admin/)
admin.site.site_header = 'Lanchonete - Administração'
admin.site.site_title = 'Lanchonete Admin'
admin.site.index_title = 'Gerenciamento do cardápio'


# TabularInline: mostra os produtos em forma de tabela DENTRO da tela da categoria
class ProdutoInline(admin.TabularInline):
    model = Produto
    extra = 1  # quantas linhas vazias aparecem para cadastrar novos produtos
    fields = ['nome', 'preco', 'disponivel']


# @admin.register(Model) é o mesmo que admin.site.register(Model, ClasseAdmin)
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'quantidade_produtos']
    search_fields = ['nome']
    inlines = [ProdutoInline]

    # Coluna calculada: usa o related_name para contar os produtos
    @admin.display(description='Qtd. de produtos')
    def quantidade_produtos(self, obj):
        return obj.produtos.count()


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'categoria', 'disponivel']  # colunas da listagem
    list_filter = ['categoria', 'disponivel']  # filtros na lateral direita
    search_fields = ['nome']  # caixa de busca
    list_editable = ['disponivel']  # dá para marcar/desmarcar direto na listagem
    actions = ['marcar_indisponivel', 'marcar_disponivel']

    # Action: aparece no menu "Ação" ao selecionar produtos na listagem
    @admin.action(description='Marcar como indisponível')
    def marcar_indisponivel(self, request, queryset):
        total = queryset.update(disponivel=False)
        self.message_user(request, f'{total} produto(s) marcado(s) como indisponível.')

    @admin.action(description='Marcar como disponível')
    def marcar_disponivel(self, request, queryset):
        total = queryset.update(disponivel=True)
        self.message_user(request, f'{total} produto(s) marcado(s) como disponível.')


# Formulário do admin de AreaEntrega com a mesma validação do serializer (consulta o IBGE)
class AreaEntregaForm(forms.ModelForm):
    class Meta:
        model = AreaEntrega
        fields = '__all__'

    def clean_codigo_ibge(self):
        codigo = self.cleaned_data['codigo_ibge']
        try:
            existe = municipio_existe(codigo)
        except IBGEIndisponivel:
            raise forms.ValidationError('O IBGE não respondeu. Tente salvar novamente mais tarde.')
        if not existe:
            raise forms.ValidationError(f'O código {codigo} não existe no IBGE.')
        return codigo


@admin.register(AreaEntrega)
class AreaEntregaAdmin(admin.ModelAdmin):
    form = AreaEntregaForm
    list_display = ['municipio', 'codigo_ibge', 'taxa_entrega']
    search_fields = ['municipio']
    list_editable = ['taxa_entrega']
