# Run via Praat > Open Praat script, then Run. Paths are relative to this script.
form Open guitar annotation
    integer Guitar_number 4
endform
if guitar_number < 1 or guitar_number > 10
    exitScript: "Choose a guitar number from 1 to 10."
endif
id$ = "GTR" + right$("00" + string$(guitar_number), 3)
Read from file: "../data/audio/" + id$ + ".wav"
sound = selected("Sound")
Read from file: "../annotations/audio/" + id$ + ".TextGrid"
grid = selected("TextGrid")
selectObject: sound, grid
View & Edit
