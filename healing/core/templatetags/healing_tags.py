from django import template

register = template.Library()


@register.filter
def mascarar_cpf(cpf):
    if not cpf or len(cpf) < 11:
        return cpf
    return f'***.{cpf[3:6]}.{cpf[6:9]}-**'


@register.filter
def formatar_cpf(cpf):
    if not cpf or len(cpf) < 11:
        return cpf
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'


@register.filter
def perfil_badge_cor(perfil):
    cores = {
        'admin': 'badge-purple',
        'medico': 'badge-cyan',
        'recepcionista': 'badge-green',
    }
    return cores.get(perfil, 'badge-gray')


@register.filter
def status_badge_cor(status):
    cores = {
        'agendada': 'badge-amber',
        'realizada': 'badge-green',
        'cancelada': 'badge-red',
    }
    return cores.get(status, 'badge-gray')
