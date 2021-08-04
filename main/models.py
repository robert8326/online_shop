from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from PIL import Image
from django.urls import reverse

User = get_user_model()


# *********
# 1 Categoty
# 2 Product
# 3 CartProduct
# 4 Cart
# 5 Order
# **********
# 6 Customer


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class LatestProductsManager:
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                return sorted(
                    products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                )
        return products


class LatestProducts:
    objects = LatestProductsManager()


class CategoryManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_left_sidebar(self):
        qs = self.get_queryset().annotate(models.Count('slug'))
        print(qs[0].slug__count)


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    objects = CategoryManager()
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Имя категории'
        verbose_name_plural = 'Имя категории'


class Product(models.Model):
    class Meta:
        abstract = True

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    MAX_IMAGE_SIZE = 3145728

    categoty = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Название товара')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описани', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    # def save(self, *args, **kwargs):
    #     image = self.image
    #     img = Image.open(image)
    #     min_height, min_width = self.MIN_RESOLUTION
    #     max_height, max_width = self.MAX_RESOLUTION
    #     if img.height < min_height or img.width < min_width:
    #         raise MinResolutionErrorException('Разрешение изображения меньше минимального')
    #     if img.height > max_height or img.width > max_width:
    #         raise MaxResolutionErrorException('Разрешение изображения больше максимального')
    #     super().save(*args, **kwargs)


class NotebookProduct(Product):
    diogonal = models.CharField(max_length=255, verbose_name='Диоганаль')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    processor_freq = models.CharField(max_length=255, verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    video = models.CharField(max_length=255, verbose_name='Видеокарта')
    time_without_change = models.CharField(max_length=255, verbose_name='Время работы аккумулятора')

    def __str__(self):
        return '{} : {}'.format(self.categoty.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class SmartPhoneProduct(Product):
    diogonal = models.CharField(max_length=255, verbose_name='Диоганаль')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    resolution = models.CharField(max_length=255, verbose_name='Расшерение экрана')
    accum_volume = models.CharField(max_length=255, verbose_name='Объем батареи')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    sd = models.BooleanField(default=True, verbose_name='Наличии sd карты')
    sd_volume_max = models.CharField(max_length=255, null=True, blank=True, verbose_name='Максимальный объём')
    main_cam_mp = models.CharField(max_length=255, verbose_name='Главная камера')
    frontal_cam_mp = models.CharField(max_length=255, verbose_name='Фронтальная камера')

    def __str__(self):
        return '{} : {}'.format(self.categoty.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_product')
    # product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return 'Товар: {} (для корзины)'.format(self.content_object.title)

    class Meta:
        verbose_name = 'Карта продукта'
        verbose_name_plural = 'Карта продуктов'


class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)
    product = models.ManyToManyField(CartProduct, blank=True, related_name='related_card')
    totle_product = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __srt__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Карта'
        verbose_name_plural = 'Карты'


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=25, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адресс')

    def __str__(self):
        return 'Покупатель: {} {}'.format(self.user.first_name, self.user.last_name)

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Пользователи'

# class Specification(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     name = models.CharField(max_length=255, verbose_name='Имя товара для харнения')
#
#     def __str__(self):
#         return 'Характеристика для товара: {}'.format(self.name)
#
# class Meta:
#     verbose_name = 'Характеристики'
#     verbose_name_plural = 'Характеристики'
