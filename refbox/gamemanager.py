class GameState(object):
    game_over = 0
    first_half = 1
    half_time = 2
    second_half = 3


class TimeoutState(object):
    none = 0
    ref = 1
    white = 2
    black = 3


class GameManager(object):

    def __init__(self):
        self._white_score = 0
        self._black_score = 0
        self._game_clock = 0
        self._is_clock_running = False
        self._game_state = GameState.game_over
        self._timeout_state = TimeoutState.none

    def gameClock(self):
        return self._game_clock

    def setGameClock(self, n):
        self._game_clock = n

    def whiteScore(self):
        return self._white_score

    def setWhiteScore(self, n):
        self._white_score = n

    def blackScore(self):
        return self._black_score

    def setBlackScore(self, n):
        self._black_score = n

    def gameClockRunning(self):
        return self._is_clock_running

    def setGameClockRunning(self, b):
        self._is_clock_running = b

    def gameState(self):
        return self._game_state

    def setGameState(self, state):
        self._game_state = state

    def timeoutState(self):
        return self._timeout_state

    def setTimeoutState(self, state):
        self._timeout_state = state

    def gameStateFirstHalf(self):
        return self._game_state == GameState.first_half

    def setGameStateFirstHalf(self):
        self._game_state = GameState.first_half

    def gameStateHalfTime(self):
        return self._game_state == GameState.half_time

    def setGameStateHalfTime(self):
        self._game_state = GameState.half_time

    def gameStateSecondHalf(self):
        return self._game_state == GameState.second_half

    def setGameStateSecondHalf(self):
        self._game_state = GameState.second_half

    def gameStateGameOver(self):
        return self._game_state == GameState.game_over

    def setGameStateGameOver(self):
        self._game_state = GameState.game_over

    def timeoutStateNone(self):
        return self._timeout_state == TimeoutState.none

    def setTimeoutStateNone(self):
        self._timeout_state = TimeoutState.none

    def timeoutStateRef(self):
        return self._timeout_state == TimeoutState.ref

    def setTimeoutStateRef(self):
        self._timeout_state = TimeoutState.ref

    def timeoutStateBlack(self):
        return self._timeout_state == TimeoutState.black

    def setTimeoutStateBlack(self):
        self._timeout_state = TimeoutState.black

    def timeoutStateWhite(self):
        return self._timeout_state == TimeoutState.white

    def setTimeoutStateWhite(self):
        self._timeout_state = TimeoutState.white
