from .gamemanager import GameManager

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

    mgr.setGameClockRunning(True)
    assert mgr.gameClockRunning() is True

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

def test_gameStateRefTimeOut():
    mgr = GameManager()
    assert mgr.gameStateRefTimeOut() is False

    mgr.setGameStateRefTimeOut()
    assert mgr.gameStateRefTimeOut() is True

