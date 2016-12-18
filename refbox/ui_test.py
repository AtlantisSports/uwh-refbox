from . import ui
from .gamemanager import GameManager
from .noiomanager import IOManager
from mock import patch
import sys

tk = 'Tkinter' if sys.version_info < (3,) else 'tkinter'

def test_sized_frame():
    assert ui.sized_frame(None, 1, 2)


def test_score_column():
    root = ui.sized_frame(None, 1, 2)
    assert ui.ScoreColumn(root, 2, 'black', 'blue', 5, lambda: 42, lambda: 43)


def test_normal_view():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    assert nv.first_game_started is False


def test_edit_score():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.edit_score()


@patch('{}.Toplevel.mainloop'.format(tk))
def test_change_clicked(mainloop):
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.score_change_clicked()


def test_edit_time():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.mgr.setGameClock(2)
    nv.edit_time(1)
    assert nv.mgr.gameClock() == 2


@patch('{}.Toplevel.mainloop'.format(tk))
def test_ref_timeout_clicked(mainloop):
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.ref_timeout_clicked()

    # Assert the clock is restarted on resume()
    assert nv.mgr.gameClockRunning() is True
