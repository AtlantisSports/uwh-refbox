from . import ui
from .gamemanager import GameManager
from .noiomanager import IOManager

def test_game_config_parser():
    cfg = ui.GameConfigParser()
    assert type(cfg.getint('game', 'half_play_duration')) == int
    assert type(cfg.getint('game', 'half_time_duration')) == int

def test_sized_frame():
    assert ui.sized_frame(None, 1, 2)


def test_score_column():
    root = ui.sized_frame(None, 1, 2)
    assert ui.ScoreColumn(root, 2, 'black', 'blue', 5, lambda: 42, lambda: 43, lambda: 44)


def test_normal_view():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    assert nv.mgr.gameClockRunning() is False
    assert nv.mgr.gameClock() > 0

    nv.gong_clicked()
    assert nv.mgr.gameClockRunning() is True

def test_game_over():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.mgr.setGameStateSecondHalf()
    nv.mgr.setGameClock(0)
    nv.mgr.setGameClockRunning(True)

    nv.refresh_time()
    assert nv.mgr.gameStateGameOver() is True
    assert nv.mgr.gameClockRunning() is False

def test_edit_score():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.edit_white_score()
    nv.edit_black_score()


def test_inc_score():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.increment_white_score()
    nv.increment_black_score()


def test_edit_time():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.mgr.setGameClock(2)
    nv.edit_time()
    assert nv.mgr.gameClock() == 2
