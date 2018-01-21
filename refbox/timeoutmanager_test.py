from . import timeoutmanager
from .gamemanager import GameManager, GameState, TimeoutState, Penalty, TeamColor

class Observable(object):
    def __init__(self):
        self._value = None

    def get(self):
        return self._value

    def set(self, x):
        self._value = x

def test_click():
    mgr = GameManager()
    assert mgr.gameClockRunning() is False
    assert mgr.gameState() == GameState.first_half
    assert mgr.timeoutState() == TimeoutState.none

    timeout_mgr = timeoutmanager.TimeoutManager(Observable())
    assert timeout_mgr._text.get() == "START"

    # Test when button says START.
    timeout_mgr.click(mgr, 0)
    assert mgr.gameClockRunning() is True
    assert mgr.gameState() == GameState.first_half
    assert mgr.timeoutState() == TimeoutState.none
    assert timeout_mgr._text.get() == "TIMEOUT"

    # Test adding a penalty
    p = Penalty(24, TeamColor.white, 5 * 60, 10 * 60)
    mgr.addPenalty(p)
    assert len(mgr.penalties(TeamColor.white)) == 1

    # Test when button says TIMEOUT.
    timeout_mgr.click(mgr, 0)
    assert mgr.gameClockRunning() is False
    assert mgr.gameState() == GameState.first_half
    assert mgr.timeoutState() == TimeoutState.ref
    assert timeout_mgr._text.get() == "RESUME"

    # Test when button says RESUME.
    timeout_mgr.click(mgr, 0)
    assert mgr.gameClockRunning() is True
    assert mgr.gameState() == GameState.first_half
    assert mgr.timeoutState() == TimeoutState.none
    assert timeout_mgr._text.get() == "TIMEOUT"

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
    assert timeout_mgr._text.get() == "START"
    assert len(mgr.penalties(TeamColor.white)) == 0
