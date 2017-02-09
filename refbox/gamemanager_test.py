from .gamemanager import GameManager, GameState, TimeoutState


def test_gameClock():
    mgr = GameManager()
    assert mgr.gameClock() == 0

    mgr.setGameClock(1)
    assert mgr.gameClock() == 1


def test_whiteScore():
    mgr = GameManager()
    assert mgr.whiteScore() == 0

    mgr.setWhiteScore(1)
    assert mgr.whiteScore() == 1


def test_blackScore():
    mgr = GameManager()
    assert mgr.blackScore() == 0

    mgr.setBlackScore(1)
    assert mgr.blackScore() == 1


def test_gameClockRunning():
    mgr = GameManager()
    assert mgr.gameClockRunning() is False
    assert mgr._time_at_start is None

    mgr.setGameClockRunning(True)
    assert mgr.gameClockRunning() is True

    mgr.setGameClock(1)
    assert mgr._time_at_start

def test_gameStateFirstHalf():
    mgr = GameManager()
    assert mgr.gameStateFirstHalf() is False

    mgr.setGameStateFirstHalf()
    assert mgr.gameStateFirstHalf() is True


def test_gameStateHalfTime():
    mgr = GameManager()
    assert mgr.gameStateHalfTime() is False

    mgr.setGameStateHalfTime()
    assert mgr.gameStateHalfTime() is True


def test_gameStateSecondHalf():
    mgr = GameManager()
    assert mgr.gameStateSecondHalf() is False

    mgr.setGameStateSecondHalf()
    assert mgr.gameStateSecondHalf() is True


def test_gameStateGameOver():
    mgr = GameManager()
    mgr.setGameStateSecondHalf()
    assert mgr.gameStateGameOver() is False

    mgr.setGameStateGameOver()
    assert mgr.gameStateGameOver() is True


def test_timeoutStateNone():
    mgr = GameManager()
    mgr.setTimeoutStateNone()
    assert mgr.timeoutStateNone() is True

    mgr.setTimeoutStateRef()
    assert mgr.timeoutStateNone() is False


def test_timeoutStateRef():
    mgr = GameManager()
    mgr.setTimeoutStateRef()
    assert mgr.timeoutStateRef() is True

    mgr.setTimeoutStateNone()
    assert mgr.timeoutStateRef() is False


def test_gameState():
    mgr = GameManager()
    mgr.setGameState(GameState.first_half)
    assert mgr.gameState() == GameState.first_half

def test_timeoutState():
    mgr = GameManager()
    mgr.setTimeoutState(TimeoutState.ref)
    assert mgr.timeoutState() == TimeoutState.ref
