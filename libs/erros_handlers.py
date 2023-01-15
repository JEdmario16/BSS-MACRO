class MissingConfigError(Exception):
    """
    Exceção levantada quanto uma secão ou chave não é encontrada no arquivo config.ini
    """


class RobloxNotOpenError(Exception):
    """
    Exceção levantada quando o roblox não está aberto
    """
