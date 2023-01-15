from libs import macro_tools
import os
import pyautogui
from PIL import Image
from datetime import datetime, timedelta

from typing import Optional

# Variáveis globais. Quando a velocidade do player é alterada, o valor é armazenado aqui.
current_haste_stack = 0
current_haste_time = 0
configs = macro_tools.read_config()


def get_current_haste_stack(screenshot: Optional[Image.Image] = None) -> int:

    """
    Retorna a quantidade de stacks de haste que o player tem.
    Para isso, procuramos em uma captura de tela onde os buffs são exibidos por tokens de haste.
    Para evitar buscar por 10 tokens a todo momento, o haste trigger é procurado primeiro, e a partir dele, a busca
    é feita em uma área menor. Caso ele não seja encontrado, não há necessidade de descobrir a stack de haste.
    Optamos por fazer com que esta função não altere a variável global current_haste_stack, e sim retornar o valor, para termos
    mais controle sobre quando ela deve ser alterada.

    O parâmetro screenshot é opcional, e pode ser utilizado para reutilizar a imagem capturada anteriormente.
    Atualmente, o processo mais demorado é a captura de tela(aprox. 17ms), e não a busca por tokens. Por isso, é recomendado que
    a imagem seja capturada uma única vez e reutilizada.

    :param screenshot: A imagem que será usada para procurar os tokens de haste

    :return: A quantidade de stacks de haste que o player tem

    """

    assets_path = configs["PATHS"]["assets"]
    (0, 30, 600, 50)

    tokens_path = os.path.join(assets_path, "tokens\\haste\\")
    token_trigger = os.path.join(tokens_path, "haste-trigger.png")

    haste_tokens = [
        f"x{i}.png" for i in range(1, 11)
    ]  # Lista de tokens de haste
    if not screenshot:
        screenshot = macro_tools.screenshot(buffs_region)

    # tenta localizar o trigger de haste
    has_trigger = pyautogui.locate(token_trigger, screenshot, confidence=0.75)
    if has_trigger:

        # Agora que sabemos em que lugar o haste deve estar, vamos cortar a imagem para otimizar a busca
        sc2 = screenshot.crop((has_trigger[0] - 5, 0, 35 + has_trigger[0], 40))
        for stack_token in haste_tokens:
            haste_stack = pyautogui.locate(
                tokens_path + stack_token, sc2, confidence=0.98
            )
            if haste_stack:
                return haste_tokens.index(stack_token) + 1

    return 0


def check_if_bear(screenshot: Optional[Image.Image]) -> bool:
    """
    Verifica se o player está em bear form.
    Para isso, procuramos em uma captura de tela onde os buffs são exibidos por tokens de bear morph.
    Aqui, efetuamos um looping em uma lista de tokens, e retornamos True caso algum deles seja encontrado.
    Como todos os bear possuem o mesmo buff, não há necessidade de retornar qual deles é.

    O parâmetro screenshot é opcional, e pode ser utilizado para reutilizar a imagem capturada anteriormente.

    :param screenshot: A imagem que será usada para procurar os tokens de bear morph
    :return: True caso o player esteja em bear form, False caso contrário
    """

    assets_path = configs["PATHS"]["assets"]
    bear_tokens = [
        "black_bear.png",
        "brown_bear.png",
        "polar_bear.png",
        "mother_bear.png",
        "panda_bear.png",
        "science_bear.png",
        "mother_bear.png",
    ]
    buffs_region = (0, 40, 600, 40)

    if not screenshot:
        screenshot = macro_tools.screenshot(buffs_region)

    for bear_token in bear_tokens:
        bear_form = os.path.join(assets_path, "tokens\\bear\\", bear_token)
        if pyautogui.locate(bear_form, screenshot, confidence=0.85):
            return True
    return False


def update_player_movespeed() -> float:

    """
    Atualiza a velocidade do player, checando por tokens que podem dar buffs de velocidade.
    !important: Atualmente, o script NÃO tem capacidade de buscar por ``coconut_haste``, ``tornado`` e ``haste+``.

    :return: float

    """

    global current_haste_stack
    global current_haste_time

    screenshot = macro_tools.screenshot((0, 40, 600, 40))
    player_speed = int(configs["PLAYER"]["player_speed"])
    CANONICAL_SPEED = 18

    haste_stack = get_current_haste_stack(screenshot)

    if haste_stack > 0 and haste_stack != current_haste_stack:
        current_haste_stack = haste_stack
        current_haste_time = datetime.now()

    delta = (
        datetime.now() - current_haste_time
        if current_haste_time != 0
        else timedelta(seconds=0)
    )
    #! Pedaço de código em teste. O algoritimo leva um certo tempo para triggar o haste, então ele irá andar menos do que deveria. Para contornar isso,
    #! irei fazer com que o haste dure um pouco menos do que o esperado, e assim, o player irá andar por mais tempo.
    if delta.seconds >= 18:

        current_haste_stack = 0
        current_haste_time = 0

    has_bear = 1 if check_if_bear(screenshot) else 0

    # calcula a velocidade  do player
    current_player_speed = (
        (CANONICAL_SPEED + 6 * has_bear) * player_speed / CANONICAL_SPEED
    ) * (1 + 0.1 * current_haste_stack)

    return current_player_speed
