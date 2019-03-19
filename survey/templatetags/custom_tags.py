from django import template
register = template.Library()


@register.filter
def in_result(queryset, question_id):
    return queryset.filter(question_id=question_id)
