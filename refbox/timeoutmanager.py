class TimeoutManager(object):
    def __init__(self, var):
        var.set("START")
        self._text = var

    def set_game_over(self, mgr):
        self._text.set("RESET")
        mgr.setGameStateGameOver()
        mgr.setGameClockRunning(False)
        mgr.setGameClock(0)
        mgr.deleteAllPenalties()

    def click(self, mgr, half_play_duration):
        if mgr.gameStateGameOver():
            mgr.setBlackScore(0)
            mgr.setWhiteScore(0)
            mgr.setGameStateFirstHalf()
            mgr.setGameClock(half_play_duration)
            self._text.set("START")
            return

        if mgr.gameClockRunning():
            mgr.setTimeoutStateRef()
            mgr.setGameClockRunning(False)
            self._text.set('RESUME')
            return

        mgr.setTimeoutStateNone()
        mgr.setGameClockRunning(True)
        self._text.set('TIMEOUT')
