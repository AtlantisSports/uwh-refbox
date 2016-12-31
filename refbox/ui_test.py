from . import ui
from .gamemanager import GameManager
from .noiomanager import IOManager

def test_game_config_parser():
    cfg = ui.GameConfigParser()
    assert type(cfg.getint('game', 'half_play_duration')) == int
    assert type(cfg.getint('game', 'half_time_duration')) == int
    assert type(cfg.getint('game', 'game_over_duration')) == int

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


def test_change_clicked():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.score_change_clicked()


def test_edit_time():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.mgr.setGameClock(2)
    nv.edit_time(1)
    assert nv.mgr.gameClock() == 2


# FIXME: ref_timeout_clicked calls refresh_time, which puts the UI into
#        an unstable state.
#def test_ref_timeout_clicked():
#    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
#    nv.mgr.setGameClock(2)
#    nv.ref_timeout_clicked()
#
#    # Assert the clock is restarted on resume()
#    assert nv.mgr.gameClockRunning() is True
#
#    # Cleanup
#    nv.mgr.setGameClockRunning(False)
