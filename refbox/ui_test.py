from . import ui
from .gamemanager import GameManager
from .noiomanager import IOManager

def test_sized_frame():
    assert ui.sized_frame(None, 1, 2)

def test_normal_view():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    assert nv.first_game_started is False
