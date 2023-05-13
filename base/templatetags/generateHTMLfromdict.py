from django import template

register = template.Library()

@register.filter(is_safe=True)
def generateHTMLfromdict(var, post, depth=0):
    html = ""
    for topic in var:
        html += f"<p hx-post='/move-thread/{post}/{topic.id}' hx-trigger='click' hx-target='#move_thread_options'>" +  ">" * depth +  f"{topic}</p>"
        if var[topic] is not None: 
            html += generateHTMLfromdict(var[topic], post, depth+1)

    return html
