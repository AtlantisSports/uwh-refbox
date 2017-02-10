import time
import math

class GameState(object):
    game_over = 0
    first_half = 1
    half_time = 2
    second_half = 3


class TimeoutState(object):
    none = 0
    ref = 1

def now():
    return math.floor(time.time())

class GameManager(object):

    def __init__(self):
        self._white_score = 0
        self._black_score = 0
        self._duration = 0
        self._time_at_start = None
        self._game_state = GameState.first_half
        self._timeout_state = TimeoutState.none

    def gameClock(self):
        if not self.gameClockRunning():
            return self._duration

        return self._duration - (now() - self._time_at_start)

    def setGameClock(self, n):
        self._duration = n

        if self.gameClockRunning():
            self._time_at_start = now()

    def whiteScore(self):
        return self._white_score

    def setWhiteScore(self, n):
        self._white_score = n

    def blackScore(self):
        return self._black_score

    def setBlackScore(self, n):
        self._black_score = n

    def gameClockRunning(self):
        return bool(self._time_at_start)

    def setGameClockRunning(self, b):
        if b == self.gameClockRunning():
            return

        if b:
            print('game clock resumed')
            self._time_at_start = now()
        else:
            print('game clock paused')
            self._duration -= now() - self._time_at_start
            self._time_at_start = None

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
