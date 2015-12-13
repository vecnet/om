from django import template
from django.template import Context, Template

register = template.Library()


@register.simple_tag(takes_context=True)
def notifications(context):
    notifications_template = Template("""
 {% for notification in notifications %}
    <div class="container">
        <div class="row">
            <div class="span12">
                <div class="alert {{ notification.type }}">
                    {{ notification.message|safe }}
                    <button type="button" class="close" data-dismiss="alert">&times;</button>
                </div>
            </div>
        </div>
    </div>
{% endfor %}
""")
    # Retrieve the session
    try:  # try/except is needed for the server error (500) view to function
        session = context["request"].session
        if session.__contains__('notifications'):
            notifications = session.pop('notifications')
            template_context = Context({'notifications': notifications})
            return notifications_template.render(template_context)
        else:
            template_context = Context({'notifications': []})
            return notifications_template.render(template_context)
    except:
        pass
