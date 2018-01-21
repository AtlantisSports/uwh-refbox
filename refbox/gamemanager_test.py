from .gamemanager import GameManager, GameState, TimeoutState, Penalty, TeamColor

import time

_observers = [GameManager()]

def test_gameClock():
    mgr = GameManager(_observers)
    assert mgr.gameClock() == 0

    mgr.setGameClock(1)
    assert mgr.gameClock() == 1


def test_whiteScore():
    mgr = GameManager(_observers)
    assert mgr.whiteScore() == 0

    mgr.setWhiteScore(1)
    assert mgr.whiteScore() == 1


def test_blackScore():
    mgr = GameManager(_observers)
    assert mgr.blackScore() == 0

    mgr.setBlackScore(1)
    assert mgr.blackScore() == 1


def test_gameClockRunning():
    mgr = GameManager(_observers)
    assert mgr.gameClockRunning() is False
    assert mgr._time_at_start is None

    mgr.setGameClockRunning(True)
    assert mgr.gameClockRunning() is True

    time.sleep(1)

    before = mgr._time_at_start
    mgr.setGameClockRunning(True)
    assert mgr.gameClockRunning() is True
    assert before == mgr._time_at_start

    mgr.setGameClock(1)
    assert mgr._time_at_start

def test_gameStateFirstHalf():
    mgr = GameManager(_observers)
    assert mgr.gameStateFirstHalf() is True

    mgr.setGameStateSecondHalf()
    assert mgr.gameStateFirstHalf() is False


def test_gameStateHalfTime():
    mgr = GameManager(_observers)
    assert mgr.gameStateHalfTime() is False

    mgr.setGameStateHalfTime()
    assert mgr.gameStateHalfTime() is True


def test_gameStateSecondHalf():
    mgr = GameManager(_observers)
    assert mgr.gameStateSecondHalf() is False

    mgr.setGameStateSecondHalf()
    assert mgr.gameStateSecondHalf() is True


def test_gameStateGameOver():
    mgr = GameManager(_observers)
    mgr.setGameStateSecondHalf()
    assert mgr.gameStateGameOver() is False

    mgr.setGameStateGameOver()
    assert mgr.gameStateGameOver() is True


def test_timeoutStateNone():
    mgr = GameManager(_observers)
    mgr.setTimeoutStateNone()
    assert mgr.timeoutStateNone() is True

    mgr.setTimeoutStateRef()
    assert mgr.timeoutStateNone() is False


def test_timeoutStateRef():
    mgr = GameManager(_observers)
    mgr.setTimeoutStateRef()
    assert mgr.timeoutStateRef() is True

    mgr.setTimeoutStateNone()
    assert mgr.timeoutStateRef() is False


def test_gameState():
    mgr = GameManager(_observers)
    mgr.setGameState(GameState.first_half)
    assert mgr.gameState() == GameState.first_half


def test_timeoutState():
    mgr = GameManager(_observers)
    mgr.setTimeoutState(TimeoutState.ref)
    assert mgr.timeoutState() == TimeoutState.ref


def test_penalty_timeRemaining():
    p = Penalty(24, TeamColor.white, 5 * 60, 10 * 60)

    assert p.timeRemaining(10 * 60) == 5 * 60
    assert p.timeRemaining(9 * 60) == 4 * 60
    assert p.timeRemaining(8 * 60) == 3 * 60
    assert p.timeRemaining(7 * 60) == 2 * 60
    assert p.timeRemaining(6 * 60) == 1 * 60
    assert p.timeRemaining(5 * 60) == 0
    assert p.timeRemaining(4 * 60) == 0
    assert p.timeRemaining(3 * 60) == 0
    assert p.timeRemaining(2 * 60) == 0
    assert p.timeRemaining(1 * 60) == 0
    assert p.timeRemaining(0) == 0

def test_penalty_servedCompletely():
    p = Penalty(24, TeamColor.white, 5 * 60, 10 * 60)

    assert not p.servedCompletely(10 * 60)
    assert not p.servedCompletely(5 * 60 + 1)
    assert p.servedCompletely(5 * 60)
    assert p.servedCompletely(0)

def test_penalty_dismissed():
    p = Penalty(24, TeamColor.white, -1, 10 * 60)

    assert p.dismissed()

def test_penalty_getters():
    p = Penalty(24, TeamColor.white, 5 * 60, 10 * 60)

    assert p.player() == 24
    assert p.team() == TeamColor.white
    assert p.startTime() == 10 * 60
    assert p.duration() == 5 * 60


def test_addPenalty():
    p = Penalty(24, TeamColor.white, 5 * 60)
    mgr = GameManager()

    mgr.addPenalty(p)
    assert len(mgr.penalties(TeamColor.white)) == 1
    assert len(mgr.penalties(TeamColor.black)) == 0

    mgr.delPenalty(p)
    assert len(mgr.penalties(TeamColor.white)) == 0
    assert len(mgr.penalties(TeamColor.black)) == 0


def test_penaltyStateChange():
    mgr = GameManager()
    p = Penalty(24, TeamColor.white, 5 * 60)
    mgr.addPenalty(p)

    mgr.pauseOutstandingPenalties()
    mgr.setGameStateHalfTime()
    assert len(mgr.penalties(TeamColor.white)) == 1

    mgr.setGameStateSecondHalf()
    mgr.restartOutstandingPenalties()
    assert len(mgr.penalties(TeamColor.white)) == 1

    mgr.setGameStateGameOver()
    mgr.deleteAllPenalties()
    assert len(mgr.penalties(TeamColor.white)) == 0

def test_penalty_start():
    p = Penalty(24, TeamColor.white, 5 * 60)
    mgr = GameManager()

    mgr.setGameClock(10 * 60)

    mgr.addPenalty(p)
    mgr.setGameClockRunning(True)
    mgr.setGameClockRunning(False)

    before = p.timeRemaining(mgr.gameClock())
    mgr.setGameClock(mgr.gameClock() - 1)
    assert 1 + p.timeRemaining(mgr.gameClock()) == before

def test_penalty_setPlayer():
    p = Penalty(24, TeamColor.white, 5 * 60)

    assert p.player() == 24
    p.setPlayer(42)
    assert p.player() == 42

def test_penalty_duration():
    p = Penalty(24, TeamColor.white, 5 * 60)

    assert p.duration() == 5 * 60
    p.setDuration(4 * 60)
    assert p.duration() == 4 * 60

def test_penalty_addWhileRunning():
    mgr = GameManager()
    mgr.setGameClock(5*60)
    mgr.setGameClockRunning(True)
    p = Penalty(24, TeamColor.white, 5 * 60)
    mgr.addPenalty(p)
    before = p.timeRemaining(4 * 60)
    assert p.timeRemaining(3 * 60) + 60 == before

def test_penalty_halftime():
    mgr = GameManager()
    p = Penalty(24, TeamColor.white, 5 * 60)
    mgr.addPenalty(p)

    mgr.setGameClock(1 * 60)
    mgr.setGameClockRunning(True)
    mgr.setGameClockRunning(False)
    mgr.setGameClock(0)

    assert p.timeRemaining(mgr.gameClock()) == 4 * 60

    mgr.pauseOutstandingPenalties()
    mgr.setGameStateHalfTime()
    assert p.timeRemaining(mgr.gameClock()) == 4 * 60
    mgr.setGameClock(2 * 60)
    assert p.timeRemaining(mgr.gameClock()) == 4 * 60
    mgr.setGameClock(1 * 60)
    assert p.timeRemaining(mgr.gameClock()) == 4 * 60
    mgr.setGameClock(0 * 60)
    assert p.timeRemaining(mgr.gameClock()) == 4 * 60

    mgr.setGameStateSecondHalf()
    mgr.setGameClock(10 * 60)
    mgr.restartOutstandingPenalties()
    assert p.timeRemaining(mgr.gameClock()) == 4 * 60
    mgr.setGameClock(9 * 60)
    assert p.timeRemaining(mgr.gameClock()) == 3 * 60
    mgr.setGameClock(8 * 60)
    assert p.timeRemaining(mgr.gameClock()) == 2 * 60
    mgr.setGameClock(7 * 60)
    assert p.timeRemaining(mgr.gameClock()) == 1 * 60
    mgr.setGameClock(6 * 60)
    assert p.timeRemaining(mgr.gameClock()) == 0
