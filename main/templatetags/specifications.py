from django import template

register = template.Library()

TABLE_HEAD = """
                 <table class="table">
                     <tbody>
             """

TABLE_TAIL = """
                     </tbody>
                 </table>
             """

TABLE_CONTENT = """
                    <tr>
                      <td>{name}</td>
                      <td>{value}</td>
                    </tr>
                """


@register.filter
def product_spec(product):
    print(product)
    pass
