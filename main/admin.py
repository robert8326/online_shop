from django.forms import ModelChoiceField, ModelForm, ValidationError
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *
from PIL import Image


# class NotebookAdminForm(ModelForm):
#     MIN_RESOLUTION = (400, 400)
#     MAX_RESOLUTION = (800, 800)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['image'].help_text = mark_safe(
#             '<span style="color:red;font-size:14px">Загружайте изображение с минимальным разрешением {}x{}</span>'.format(
#                 *self.MIN_RESOLUTION))

# def clean_image(self):
#     image = self.cleaned_data['image']
#     img = Image.open(image)
#     min_height, min_width = self.MIN_RESOLUTION
#     max_height, max_width = self.MAX_RESOLUTION
#     if image.size > Product.MAX_IMAGE_SIZE:
#         raise ValidationError('Размер изображение не должен привышать 3MB!')
#     if img.height < min_height or img.width < min_width:
#         raise ValidationError('Разрешение изображения меньше минимального')
#     if img.height > max_height or img.width > max_width:
#         raise ValidationError('Разрешение изображения больше максимального')
#     return image


class SmartphoneAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not instance.sd:
            self.fields['sd_volume_max'].widget.attrs.update({
                'readonly': True,'style':'background:lightgray;'
            })

    def clean(self):
        if not self.cleaned_data['sd']:
            self.cleaned_data['sd_volume_max'] = None
        return self.cleaned_data

class NotebookAdmin(admin.ModelAdmin):
    # form = NotebookAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'categoty':
            return ModelChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartPhoneAdmin(admin.ModelAdmin):
    change_form_template = 'admin.html'
    # form = SmartphoneAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'categoty':
            return ModelChoiceField(Category.objects.filter(slug='smartphone'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(NotebookProduct, NotebookAdmin)
admin.site.register(SmartPhoneProduct, SmartPhoneAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
