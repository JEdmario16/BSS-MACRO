from win32gui import GetWindowText, GetForegroundWindow
import mss
from PIL import Image
import os
import configparser
import pyautogui
import webbrowser
import keyboard
from time import sleep
from libs.erros_handlers import RobloxNotOpenError, MissingConfigError

from typing import Optional


def get_active_window() -> str:
    return GetWindowText(GetForegroundWindow())


def kill_roblox() -> None:

    # Verifica se o roblox está aberto
    if "RobloxPlayerBeta.exe" in get_procces_by_name("RobloxPlayerBeta.exe"):
        os.system("taskkill /f /im RobloxPlayerBeta.exe")


def get_procces_by_name(name: str) -> str:
    return os.popen(f"tasklist | findstr {name}").read()


def start_roblox_in_private_server(_auto_kill: bool = True) -> bool:
    """
    Abre o roblox em um servidor privado.
    A url do servidor deve estar no arquivo config.ini. Caso não haja nenhuma url, a função irá retornar False
    Obs: A função não checa se o jogo foi aberto ou não. Ela apenas abre o roblox
    irei atribuir essa responsabilidade a quem chamar a função.

    :param _auto_kill: Se True, a função irá fechar o roblox caso ele já esteja aberto
    """

    server_url = read_config()["ROBLOX"]["private_server_url"]

    if _auto_kill:
        kill_roblox()
    if server_url:
        webbrowser.open(server_url)
        return True
    raise MissingConfigError(
        "Não foi encontrada nenhuma url no arquivo config.ini"
    )


def get_roblox_window() -> Optional[pyautogui.Window]:

    """
    Retorna a janela do roblox
    """

    try:
        roblox_window = pyautogui.getWindowsWithTitle("Roblox")[0]
        return roblox_window
    except IndexError:
        raise RobloxNotOpenError("O roblox não está aberto")  # noqa


def activate_roblox() -> None:
    """
    Ativa a janela do roblox
    """

    roblox_window = get_roblox_window()
    roblox_window.activate()


def read_config():
    """
    Lê o arquivo config.ini e retorna um dicionário com as informações
    TODO: deserializar as informacões, para não ter que setar o tipo o tipo dos valores quando for ler
    """

    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    config_filepath = os.path.join(CURRENT_PATH, "..", "config.ini")

    # Verifica se o arquivo existe
    if not os.path.exists(config_filepath):
        raise FileNotFoundError("Arquivo config.ini não encontrado")

    config = configparser.ConfigParser()
    config.read(config_filepath)
    return config


def set_value_in_config(section: str, key: str, value: str) -> None:
    """
    Altera um valor no arquivo config.ini

    :param section: A seção do arquivo config.ini
    :param key: A chave do arquivo config.ini
    :param value: O valor que será atribuído
    """

    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    config_filepath = os.path.join(CURRENT_PATH, "..", "config.ini")

    # Verifica se o arquivo existe
    if not os.path.exists(config_filepath):
        raise FileNotFoundError("Arquivo config.ini não encontrado")

    config = configparser.ConfigParser()
    config.read(config_filepath)
    config[section][key] = value

    with open(config_filepath, "w", encoding="utf-8") as configfile:
        config.write(configfile)


def screenshot(
    region: tuple[int, int, int, int], filename: str = None
) -> Image:
    """
    Captura uma imagem da tela e retorna um objeto do tipo Image do PIL
    O próprio pyautogui e o PIL são capazes de capturar a tela, mas o mss é muito mais rápido
    Em testes, o mss capturou a tela em 17ms, enquanto o pyautogui levou de 60 a 80ms
    Além disso, foi vereficado que o tempo para a screenshot do mss não aumenta consideravelmente com o tamanho da tela. No entanto,
    caso seja necessário procurar por algo na imagem, é recomendado que ``region`` seja o menor possível

    :param region: Uma tupla com as coordenadas da região que será capturada (x, y, width, height), onde x e y são as coordenadas do canto superior esquerdo
    :param filename: O nome do arquivo que será salvo. Se None, a imagem não será salva.
    """

    with mss.mss() as sct:
        # Captura a tela toda

        monitor = {
            "left": region[0],
            "top": region[1],
            "width": region[2],
            "height": region[3],
        }
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        if filename:
            img.save(filename)
        return img


def check_if_full_inventory() -> bool:

    """
    Verifica se o inventário está cheio.
    Como o espaço do inventário é mutável, ImageMatch não é uma boa opção.
    Além disso, o ``pyautogui.pixelMatchesColor`` é bem efiiciente, então é o método escolhido.
    Uma outra opção seria tirar uma screenshot da tela e procurar por uma imagem, mas isso é mais lento. \n
    ?(future-feature) Uma melhoria provavel seria a possibilidade de receber uma imagem como parâmetro, para reautilizar a imagem capturada anteriormente.
    """

    FULL_BAG_COLOR = (247, 0, 23)

    TARGET_PIXEL_POSITION = (1045, 5)

    return pyautogui.pixelMatchesColor(*TARGET_PIXEL_POSITION, FULL_BAG_COLOR)
