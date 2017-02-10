from . import ui
from .gamemanager import GameManager, GameState, TimeoutState
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


def test_ref_timeout_clicked():
    mgr = GameManager()
    assert mgr.gameClockRunning() is False
    assert mgr.gameState() == GameState.first_half
    assert mgr.timeoutState() == TimeoutState.none

    timeout_mgr = ui.TimeoutManager()
    assert timeout_mgr.text.get() == "START"

    # Test when button says START.
    timeout_mgr.click(mgr, 0)
    assert mgr.gameClockRunning() is True
    assert mgr.gameState() == GameState.first_half
    assert mgr.timeoutState() == TimeoutState.none
    assert timeout_mgr.text.get() == "TIMEOUT"

    # Test when button says TIMEOUT.
    timeout_mgr.click(mgr, 0)
    assert mgr.gameClockRunning() is False
    assert mgr.gameState() == GameState.first_half
    assert mgr.timeoutState() == TimeoutState.ref
    assert timeout_mgr.text.get() == "RESUME"

    # Test when button says RESUME.
    timeout_mgr.click(mgr, 0)
    assert mgr.gameClockRunning() is True
    assert mgr.gameState() == GameState.first_half
    assert mgr.timeoutState() == TimeoutState.none
    assert timeout_mgr.text.get() == "TIMEOUT"

    # Jump to Game Over mode.
    mgr.setBlackScore(1)
    mgr.setWhiteScore(1)
    timeout_mgr.set_game_over(mgr)
    assert mgr.blackScore() == 1
    assert mgr.whiteScore() == 1
    assert mgr.gameClockRunning() is False
    assert mgr.gameState() == GameState.game_over

    # Test when button says RESET.
    timeout_mgr.click(mgr, 0)
    assert mgr.blackScore() == 0
    assert mgr.whiteScore() == 0
    assert mgr.gameClockRunning() is False
    assert mgr.gameState() == GameState.first_half
    assert mgr.timeoutState() == TimeoutState.none
    assert timeout_mgr.text.get() == "START"
