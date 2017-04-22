Spec
====

The system must start with the clock stopped in the "First Half" state.

If the buzzer is pressed, the clock should tenatively start running and a dialog
should be displayed confirming that the game has begun. If confirmed, the tenative
clock time should become the real clock time. The displays should show the tenative
time, which assumes the buzzer was pressed to start the game and not accidental or
to test the buzzer.

If the "start" button is pressed on the refbox, the confirmation dialog should be
skipped and the clock should immediately start running.

If the clock is selected, a dialog should be displayed with the clock still running.
As the time is adjusted, the display should NOT show the adjusted time until the a
SUBMIT button is pressed. If the minus-minute button is pressed when less than a
minute remains, the time should be set to 0:00. Neither the hours nor seconds should
drop below 0 or above 59.

If the score is selected, the EditScore dialog should be displayed. As the score is
adjusted, the display should NOT show the adjusted score until the SUBMIT button is
pressed. The score should not be allowed to drop below 0 or above 99.

If "black score" or "white score" is pressed, a confirmation dialog should be
displayed. The display should NOT show the new score until the YES button is
pressed.

After the game has completed, the clock should be stopped. The score of the previous
game should be displayed until the RESET button is pressed. The display should show
state "GAME OVER" and clock 00:00. After pressing RESET, the display should show
"FIRST HALF" and the duration of the first half.
