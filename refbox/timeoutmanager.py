from uwh.gamemanager import TimeoutState, GameState

class TimeoutManager(object):
    def __init__(self, var, team_timeout_duration):
        var.set("START")
        self._text = var
        self._team_timeout_duration = team_timeout_duration
        self._clock_at_timeout = None
        self._reset_handlers = []

    def ready_to_start(self):
        return self._text.get() == "START" or self._text.get() == "RESET"

    def ready_to_resume(self):
        return self._text.get() == "RESUME"

    def set_game_over(self, mgr):
        self._text.set("RESET")
        mgr.setGameState(GameState.game_over)
        mgr.setGameClockRunning(False)
        mgr.setGameClock(0)
        mgr.deleteAllPenalties()
        mgr.delAllGoals()

    def add_reset_handler(self, callback):
        self._reset_handlers += [callback]

    def reset(self, mgr, get_half_play_duration):
        mgr.setBlackScore(0)
        mgr.setWhiteScore(0)
        mgr.setGameState(GameState.pre_game)
        mgr.setGameClockRunning(False)
        mgr.setGameClock(get_half_play_duration())
        mgr.deleteAllPenalties()
        mgr.delAllGoals()
        for handler in self._reset_handlers:
            handler()
        self._text.set("START")

    def set_ready(self, mgr):
        self._clock_at_timeout = None
        self._text.set("RESUME")

    def click(self, mgr, get_half_play_duration, state):
        if mgr.gameState() == GameState.game_over:
            self.reset(mgr, get_half_play_duration)
            return

        if mgr.gameState() == GameState.pre_game:
            mgr.setGameState(GameState.first_half)

        if mgr.timeoutState() == TimeoutState.none and state != TimeoutState.none:
            self._clock_at_timeout = mgr.gameClock()
            mgr.pauseOutstandingPenalties()
            mgr.setGameClockRunning(False)
            mgr.setTimeoutState(state)
            if (state == TimeoutState.white or
                state == TimeoutState.black):
                mgr.setGameClock(self._team_timeout_duration())
                mgr.setGameClockRunning(True)
            self._text.set('RESUME')
            return

        mgr.setGameClockRunning(True)
        if self._clock_at_timeout is not None:
            mgr.setGameClock(self._clock_at_timeout)
            self._clock_at_timeout = None
        mgr.restartOutstandingPenalties()
        mgr.setTimeoutState(TimeoutState.none)
        self._text.set('TIMEOUT')
