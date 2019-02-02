# SUPERCELL

## A Grid instrument and sequencer for live music creation and performance

### Introduction

### Examples

- https://soundcloud.com/oddsockmachine/droplets

- https://www.youtube.com/watch?v=3huPQ8svOUQ

- https://www.youtube.com/watch?v=pdu7UI-fMRo

### Installation

`python3 -m venv ./venv && source venv/bin/activate`

`pip install -r requirements.txt`

`python controller.py [--hw 1]`

`python controller.py --set saved/2019-01-15\ 14:35:59.json`

### Usage

The instrument's layout is divided into four major sections:

- Grid, on the left
- Instrument Selector, in the middle
- Page Controls, on the right
- Scale Controls, along the bottom

#### Grid

The grid is a piano-roll style input for the sequencer

#### Z-mode
- normally time moves along the x-axis, pitch on y, instruments on z.
- Live performance mode with instruments along x, pitch on y, time steps through z.
- In other words, the ability to play all 16 instruments in real time

#### Controls

- Q quit
- s toggle_save
- S save
- [sapce] step_beat
- \` clear_page
- n cycle_key -1
- m cycle_key 1
- [ change_division -1
- ] change_division 1
- v cycle_scale -1
- b cycle_scale 1
- c swap_drum_inst
- z change_octave -1
- x change_octave 1
- r random_rpt
- t sustain
- o chaos +1
- p -1 chaos
- / toggle z mode