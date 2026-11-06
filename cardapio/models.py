from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


# Um model é uma classe Python que representa uma TABELA no banco de dados.
# Cada atributo (nome, descricao...) vira uma COLUNA dessa tabela.
# Depois de mexer aqui, rode:
#   python manage.py makemigrations  -> gera o "plano" de alteração do banco
#   python manage.py migrate         -> aplica esse plano no banco de verdade


class Categoria(models.Model):
    # unique=True: o banco não deixa existir duas categorias com o mesmo nome
    nome = models.CharField(max_length=100, unique=True)
    # blank=True: o campo pode ficar vazio nos formulários (admin e API)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ['nome']  # ordem padrão nas consultas
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        # É o texto que aparece quando o objeto é exibido (ex.: no admin)
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=150)
    # DecimalField é melhor que FloatField para dinheiro (não tem erro de arredondamento)
    # MinValueValidator garante preço >= 0 também no admin.
    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    disponivel = models.BooleanField(default=True)
    # ForeignKey = relacionamento "muitos para um": vários produtos pertencem a UMA categoria.
    # on_delete=models.PROTECT: impede apagar uma categoria que ainda tem produtos
    #   (outras opções: CASCADE apaga os produtos junto, SET_NULL deixa sem categoria).
    # related_name='produtos': permite fazer categoria.produtos.all()
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='produtos',
    )

    class Meta:
        ordering = ['nome']
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.nome


class AreaEntrega(models.Model):
    """Extra C5: municípios onde a lanchonete faz entrega."""

    municipio = models.CharField(max_length=150)
    # O código do IBGE identifica o município de forma única (7 dígitos)
    codigo_ibge = models.PositiveIntegerField(unique=True)
    taxa_entrega = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )

    class Meta:
        ordering = ['municipio']
        verbose_name = 'Área de entrega'
        verbose_name_plural = 'Áreas de entrega'

    def __str__(self):
        return self.municipio
