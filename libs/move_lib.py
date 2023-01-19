from libs import macro_tools
import os
import pyautogui
from PIL import Image
from datetime import datetime, timedelta
from time import sleep
import keyboard

from typing import Optional

# Variáveis globais. Quando a velocidade do player é alterada, o valor é armazenado aqui.
current_haste_stack = 0
current_haste_time = 0
configs = macro_tools.read_config()
BUFFS_REGION = (0, 35, 600, 40)


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

    tokens_path = os.path.join(assets_path, "tokens\\haste\\")
    token_trigger = os.path.join(tokens_path, "haste-trigger.png")

    haste_tokens = [
        f"x{i}.png" for i in range(1, 11)
    ]  # Lista de tokens de haste
    if not screenshot:
        screenshot = macro_tools.screenshot(region=BUFFS_REGION)

    # tenta localizar o trigger de haste
    has_trigger = pyautogui.locate(token_trigger, screenshot, confidence=0.75)
    if has_trigger:

        # Agora que sabemos em que lugar o haste deve estar, vamos cortar a imagem para otimizar a busca
        sc2 = screenshot.crop((has_trigger[0] - 5, 0, 35 + has_trigger[0], 40))
        for stack_token in haste_tokens:
            haste_stack = pyautogui.locate(
                tokens_path + stack_token, sc2, confidence=0.9
            )
            if haste_stack:
                return haste_tokens.index(stack_token) + 1
        else:
            print("Haste trigger encontrado, mas não foi possível encontrar a haste stack")
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

    if not screenshot:
        screenshot = macro_tools.screenshot(region=BUFFS_REGION)

    for bear_token in bear_tokens:
        bear_form = os.path.join(assets_path, "tokens\\bear\\", bear_token)
        if pyautogui.locate(bear_form, screenshot, confidence=0.85):
            return True
    return False


def move_tile(
    current_speed: float,
    direction: str,
    block_size_smooth: Optional[float] = 1,
) -> None:
    """
    Move o player ao equivalente a um tile. O tamanho do tile é de 4 studs, enquanto a velocidade do player no arquivo de configuração é em studs por segundo.
    Optei por fazer esta função detecte a velocidade do player, e então movimentar o player de acordo com a velocidade dele.
    Além disso, o parâmetro block_size_smooth é opcional, e pode ser utilizado para fazer com que o player ande mais rápido ou mais devagar.
    Isto porque durante as movimentações do player, há dessincronização, e a quantidade de blocos pode acabar sendo diferente do esperado.
    Nestes caso, uma sugestão interessante é utilizar block_size_smooth como uma progressão geométrica, que irá aumentar/diminuir a velocidade do player a uma fração de tiles.

    :param direction: direção que o player deve andar. Deve ser algo entre ['w', 'a', 's', 'd']
    :param block_size_smooth: multiplicador de tamanho de tile. Padrão: 1
    :param: current_speed: velocidade do player. Caso none, a função irá chamar por ``get_current_movespeed``
    """


    # calcula o tamanho do tile, em pixels
    tile_size = 4 * block_size_smooth

    # move o player
    keyboard.press(direction)
    sleep(tile_size / current_speed)
    keyboard.release(direction)
