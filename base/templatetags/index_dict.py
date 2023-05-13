from django import template

register = template.Library()

@register.filter(is_safe=True)
def index_dict(var, arg): 
    try:
        return var[arg]
    except:
        return None
    
