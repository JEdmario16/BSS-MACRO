from win32gui import GetWindowText, GetForegroundWindow
import mss
from PIL import Image
import os
import configparser
import pyautogui
import webbrowser
import win32gui
import win32ui
import win32con
import numpy


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
    config.read(config_filepath, encoding="utf-8")
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


def get_program_status() -> bool:
    """
    Esta função simples busca pelo status atual do programa no arquivo config.ini
    uitas das ``foreground functions`` do programa dependem do status do programa, então é melhor ter uma função
    """


def screenshot(region: tuple[int, int, int, int], window_name: Optional[str] = "Roblox",filename:Optional[str] = None) -> Image.Image:

    """
    Captura a tela do jogo na região indicada e retorna um objeto PIL.Image
    
    :param window_name: Nome da janela do jogo. Para os propósitos desta aplicação, o nome da janela é "Roblox" por padrão
    :param region: Região da tela que será capturada, (x, y, width, height)
    :param filename: Nome do arquivo que será salvo. Se None, não salva o arquivo
    :return: Objeto PIL.Image

    """

    x, y, w, h = region
    
    hwnd = win32gui.FindWindow(None, window_name)
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(w, h) , dcObj, (x,y), win32con.SRCCOPY)
    
    # Salva o bitmap diretamente como um objeto PIL.Image
    buffer = dataBitMap.GetBitmapBits(True)
    img = Image.frombytes("RGB", (w, h), buffer, "raw", "BGRX")
    

    if filename:
        img.save(filename)

    #Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

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
