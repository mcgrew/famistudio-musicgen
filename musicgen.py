#!/usr/bin/env python3

from random import random, randint, choice
from sys import argv, stdout, stderr, exit
from argparse import ArgumentParser
from io import StringIO
from typing import IO, List

NOTES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
MINOR = (0, 2, 3, 5, 7, 8, 10)
MELODIC_MINOR = (0, 2, 3, 5, 7, 9, 10)
HARMONIC_MINOR = (0, 2, 3, 5, 8, 9, 10)
MINOR_PENTATONIC = (0, 3, 5, 7, 10)
MAJOR = (0, 2, 4, 5, 7, 9, 11)
MAJOR_PENTATONIC = (0, 2, 4, 7, 9)
SCALES = {
        'major': MAJOR,
        'minor': MINOR,
#          'melodic minor': MELODIC_MINOR,
#          'harmonic minor': HARMONIC_MINOR,
        'major pentatonic': MAJOR_PENTATONIC,
        'minor pentatonic': MINOR_PENTATONIC
        }
PENT_SCALES = {
        'major pentatonic': MAJOR_PENTATONIC,
        'minor pentatonic': MINOR_PENTATONIC
        }

TEMPLATE = """Project Version="2.2.1" TempoMode="FamiStudio" Name="Untitled" Author="musicgen" Copyright="2020"
	Instrument Name="Lead0"
		Envelope Type="Volume" Length="4" Values="12,10,8,6"
		Envelope Type="DutyCycle" Length="1" Values="0"
	Instrument Name="Lead1"
		Envelope Type="Volume" Length="4" Values="12,10,8,6"
		Envelope Type="DutyCycle" Length="1" Values="1"
	Instrument Name="Lead2"
		Envelope Type="Volume" Length="4" Values="12,10,8,6"
		Envelope Type="DutyCycle" Length="1" Values="2"
	Instrument Name="NoiseBassDrum"
		Envelope Type="Volume" Length="6" Values="15,12,9,6,3,0"
		Envelope Type="DutyCycle" Length="1" Values="1"
	Instrument Name="NoiseCrash"
		Envelope Type="Volume" Length="30" Values="8,9,10,10,10,9,9,8,8,7,7,6,6,5,5,5,4,4,4,3,3,3,2,2,2,2,1,1,1,0"
	Instrument Name="NoiseHiHat"
		Envelope Type="Volume" Length="6" Values="8,6,5,4,2,0"
	Instrument Name="NoiseSnare"
		Envelope Type="Volume" Length="6" Values="7,7,7,7,7,0"
	Instrument Name="TriBass"
"""

# Create a constant tuple for all notes.
ALL_NOTES = []
for i in range(0, 8):
    for n in NOTES:
        ALL_NOTES.append(f'{n}{i}')
ALL_NOTES = tuple(ALL_NOTES)

NOTES_PER_PATTERN = 16

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('filename', nargs='?', help='The filename to save to. '
            'Output goes to stdout if no file is specified.')
    parser.add_argument('-a', '--all-scales', action='store_true',
            help='Use all scales instead of just pentatonic scales')
    parser.add_argument('--pc', '--pattern-count', type=int, default=16, metavar='COUNT',
            help="Generate this number of patterns for each song. Default is 16.")
    parser.add_argument('-s', '--songs', type=int, default=10,
            help='The number of songs to create. Default is 10.')
    parser.add_argument('-c', '--max-change', type=int, default=3,
            help='The maximum number of notes to move on the scale when generating '
                'a new note. The default is 3. There is still a chance of '
                'jumping to a random note for more variety.')
    parser.add_argument('--min-note-length', type=int, default=8, metavar='FRAMES',
            help='The minimum number of frames per note in a song. The default is 8.')
    parser.add_argument('--max-note-length', type=int, default=12, metavar='FRAMES',
            help='The maximum number of frames per note in a song. The default is 12.')

    parser.add_argument('--min-octave', type=int, default=1, metavar='OCTAVE',
            help='The lowest octave to use. The default is 1.')
    parser.add_argument('--max-octave', type=int, default=4, metavar='OCTAVE',
            help='The highest octave to use. The default is 4.')
    parser.add_argument('--tri-max-octave', type=int, default=4, metavar='OCTAVE',
            help='The highest octave to use for the triangle wave channel. '
                'The default is 4.')

    parser.add_argument('--sq1-repeat-at', type=int, default=0, metavar='PATTERN',
            help='Forces square wave track 1 to start repeating after the given number '
            'of patterns. This works best if it is a factor of pattern count. '
            'The default is 0 (do not repeat).')
    parser.add_argument('--sq2-repeat-at', type=int, default=0, metavar='PATTERN',
            help='Forces square wave track 1 to start repeating after the given number '
            'of patterns. This works best if it is a factor of pattern count. '
            'The default is 0 (do not repeat).')
    parser.add_argument('--tri-repeat-at', type=int, default=0, metavar='PATTERN',
            help='Forces triangle wave track to start repeating after the given number '
            'of patterns. This works best if it is a factor of pattern count. '
            'The default is 0 (do not repeat).')
    parser.add_argument('--pp', '--percussion-patterns', type=int, default=1,
            help='The number of percussion patterns to generate. This works '
            'best if it is a factor of pattern count. The default is 1.')

    parser.add_argument('-n', '--sq1-new-note-chance', type=float, default=0.35, metavar='CHANCE',
            help='The chance to generate a new note at each beat. Default is 0.35')
    parser.add_argument('-q', '--sq2-new-note-chance', type=float, default=0.35, metavar='CHANCE',
            help='The chance to generate a new note at each beat. Default is 0.35')
    parser.add_argument('-t', '--tri-new-note-chance', type=float, default=0.3, metavar='CHANCE',
            help='The chance to generate a new note at each beat on the triangle '
            'wave channel. Default is 0.3.')
    parser.add_argument('-p', '--stop-note-chance', type=float, default=0.2, metavar='CHANCE',
            help='The chance to generate a stop note when creating a new note. '
            'Default is 0.2')

    parser.add_argument('--scale', type=str, default=None,
            help='Print the notes in a scale to the command line and exit. '
            'e.g. "C major" or "F# minor".')
    return parser.parse_args()

class Track:
    def __init__(self, channel:str, instrument:str, note_length:int=10,
            new_note_chance:float=0.4, stop_chance:float=0.0, **kwargs):
        self.channel = channel
        self.instrument = instrument
        self.note_length = note_length
        self.new_note_chance = new_note_chance
        self.stop_chance = stop_chance
        for arg,value in kwargs.items():
            setattr(self, arg, value)

    def note_generator(self):
        current = choice(self.scale)
        yield current
        while True:
            if random() < 1/16:
                current = choice(self.scale)
            else:
                idx = self.scale.index(current)
                current = choice(self.scale[max(0,idx-3):idx+4])
            yield current

    def generate(self):
        self.note_count = self.repeat_at * NOTES_PER_PATTERN
        self.notes = {}
        note = self.note_generator()
        stopped = False
        for i in range(self.note_count):
            if random() > self.new_note_chance: # chance of generating a new note
                continue
            if random() > self.stop_chance: # chance of a stop note
                self.add_note(i * self.note_length, next(note))
                stopped = False
            else:
                if not stopped:
                    self.add_stop_note(i * self.note_length)
                    stopped = True
        return self

    def add_stop_note(self, time:int):
        self.notes[time] = None

    def add_note(self, time:int, note:str):
        self.notes[time] = note

    def note_at(self, time:int):
        times = sorted(self.notes.keys())
        ret = times[0]
        for t in times:
            if t > time:
                break
            ret = t
        return ret, self.notes[ret]

    def __str__(self):
        buf = StringIO()
        buf.write(f'\t\tChannel Type="{self.channel}"\n')
        for i in range(self.note_count):
            if not i % NOTES_PER_PATTERN:
                buf.write(f'\t\t\tPattern Name="Pattern {i//NOTES_PER_PATTERN}"\n')
            time = self.note_length * i
            if time not in self.notes:
                continue
            note = self.notes[time]
            if note:
                buf.write('\t\t\t\tNote '
                    f'Time="{(i%NOTES_PER_PATTERN) * self.note_length}" '
                    f'Value="{note}" Instrument="{self.instrument}"\n')
            else:
                buf.write('\t\t\t\tNote '
                    f'Time="{(i%NOTES_PER_PATTERN) * self.note_length}" Value="Stop"\n')
        for i in range(args.pc):
            buf.write(f'\t\t\tPatternInstance Time="{i}" Pattern="Pattern {i % self.repeat_at}"\n')
        buf.seek(0)
        return buf.read()

def percussion_instrument():
    instr = ("NoiseBassDrum", "NoiseBassDrum", "NoiseBassDrum", "NoiseBassDrum",
             "NoiseBassDrum", "NoiseHiHat",    "NoiseSnare",    "NoiseCrash")
    note = ("G2", "G2", "G2", "G2", "G2", "E3", "F4", "F3")
    idx = randint(0, len(instr)-1)
    return instr[idx], note[idx]

def print_scale(scale_name:str):
    if ' ' not in scale_name:
        stderr.write(f"Invalid scale '{scale_name}'\n")
        exit(-1)
    root, scale_name = scale_name.split(maxsplit=1)
    scale_name = scale_name.lower()
    if scale_name not in SCALES:
        stderr.write(f'Unknown scale. Please specify one of {", ".join(SCALES.keys())}.\n')
        exit(-1)
    if root not in NOTES:
        stderr.write(f"Invalid note '{root}'\n")
        exit(-1)
    scale = SCALES[scale_name]
    offset = NOTES.index(root)
    stdout.write(f'    {" ".join([NOTES[(x+offset)%12] for x in scale])}\n')
    exit()

def create_scale(scale:List[int], min_octave:int, max_octave:int, offset:int):
    full_scale = []
    scale_indices = sorted([(x+offset)%12 for x in scale])
    for i in range(min_octave, max_octave+1):
        for j in scale_indices:
            octave = i
            full_scale.append(f'{NOTES[j]}{octave}')
    return full_scale

def percussion_track(note_length, percussion_patterns, pattern_count):
    # Percussion track
    buf = StringIO()
    buf.write('\t\tChannel Type="Noise"\n')
    for j in range(0, percussion_patterns):
        buf.write(f'\t\t\tPattern Name="Pattern {j}"\n')
        for i in range(0, pattern_count, 2):
            if random() < 0.5:
                instr, note = percussion_instrument()
                buf.write(f'\t\t\t\tNote Time="{(i%NOTES_PER_PATTERN) * note_length}" Value="{note}" Instrument="{instr}"\n')
    for i in range(pattern_count):
        buf.write(f'\t\t\tPatternInstance Time="{i}" Pattern="Pattern {i % percussion_patterns}"\n')
    buf.seek(0)
    return buf.read()


def main():
    if args.scale:
        print_scale(args.scale)
    if args.filename:
        out = open(args.filename, 'w')
    else:
        out = stdout
    out.write(TEMPLATE)
    for song in range(args.songs):
        note_length = randint(args.min_note_length, args.max_note_length)
        offset = randint(0, 11)
        root = NOTES[offset]
        if args.all_scales:
            scale_name, which_scale = choice(list(SCALES.items()))
        else:
            scale_name, which_scale = choice(list(PENT_SCALES.items()))
        scale_name = f'{root} {scale_name}'
        octave_size = len(which_scale)
        args.sq1_repeat_at = args.sq1_repeat_at or args.pc
        args.sq2_repeat_at = args.sq2_repeat_at or args.pc
        args.tri_repeat_at = args.tri_repeat_at or args.pc

        sq1_scale = create_scale(which_scale, args.min_octave+1, args.max_octave, offset)
        sq2_scale = create_scale(which_scale, args.min_octave, args.max_octave-1, offset)
        tri_scale = create_scale(which_scale, args.min_octave, args.tri_max_octave, offset)

        out.write(f'\tSong Name="{song:02d} ({scale_name})" Length="{args.pc}" '
                f'LoopPoint="0" PatternLength="{NOTES_PER_PATTERN}" BarLength="4" NoteLength="{note_length}"\n')

        lead = randint(0, 2)
        sq1_track = Track("Square1", f'Lead{lead}', note_length,
                args.sq1_new_note_chance, args.stop_note_chance,
                repeat_at=args.sq1_repeat_at, scale=sq1_scale).generate()
        sq2_track = Track("Square2", f'Lead{lead}', note_length,
                args.sq2_new_note_chance, args.stop_note_chance,
                repeat_at=args.sq1_repeat_at, scale=sq2_scale).generate()
        tri_track = Track("Triangle", 'TriBass', note_length,
                args.tri_new_note_chance, args.stop_note_chance,
                repeat_at=args.tri_repeat_at, scale=tri_scale).generate()

        out.write(str(sq1_track))
        out.write(str(sq2_track))
        out.write(str(tri_track))

        out.write(percussion_track(note_length, args.pp, args.pc))

    if args.filename:
        out.close()

if __name__ == '__main__':
    args = parse_args()
    main()

