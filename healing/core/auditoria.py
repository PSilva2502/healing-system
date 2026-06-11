from core.middleware import obter_usuario_atual


def registrar_auditoria(tabela, operacao, dados_anteriores=None):
    from core.models import Auditoria
    usuario = obter_usuario_atual()
    Auditoria.objects.create(
        usuario=usuario,
        tabela_afetada=tabela,
        operacao=operacao,
        dados_anteriores=dados_anteriores,
    )
