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

# Createa a constant tuple for all notes.
#  ALL_NOTES = []
#  for i in range(0, 8):
#      for n in NOTES:
#          ALL_NOTES.append(f'{n}{i}')
#  ALL_NOTES = tuple(ALL_NOTES)

NOTES_PER_PATTERN = 16

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('filename', nargs='?', help='The filename to save to. '
            'Output goes to stdout if no file is specified.')
    parser.add_argument('-a', '--all-scales', action='store_true', 
            help='Use all scales instead of just pentatonic scales')
    parser.add_argument('--pattern-count', type=int, default=16, metavar='COUNT',
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
    parser.add_argument('--percussion-patterns', type=int, default=1,
            help='The number of percussion patterns to generate. This works '
            'best if it is a factor of pattern count. The default is 1.')

    parser.add_argument('-n', '--new-note-chance', type=float, default=0.35, metavar='CHANCE',
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
    def __init__(self, channel:str, repeat_at:int, scale:list, root:str, instrument:str,
            note_length:int, new_note_chance:float, stop_chance:float):
        self.channel = channel
        self.repeat_at = repeat_at or args.pattern_count
        self.note_count = self.repeat_at * NOTES_PER_PATTERN
        self.scale = scale
        self.root = root
        self.instrument = instrument
        self.note_length = note_length
        self.new_note_chance = new_note_chance
        self.stop_chance = stop_chance

    def generate(self):
        self.notes = {}
        current = randint(0, len(self.scale)-1)
        stopped = False
        for i in range(self.note_count):
            note = self.scale[current]
            if random() > self.new_note_chance: # chance of generating a new note
                continue
            if random() > self.stop_chance: # chance of a stop note
                self.add_note(i * self.note_length, note)
                stopped = False
            else:
                if not stopped:
                    self.add_note(i * self.note_length, None)
                    stopped = True
            if random() > 1/16:
                current += randint(-args.max_change, args.max_change)
                current = max(0, min(len(self.scale)-1, current))
            else:
                current = randint(0, len(self.scale)-1)
        return self

    def add_note(self, time:int, note:str):
        self.notes[time] = note

    def note_at(self, time):
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
            if time in self.notes:
                note = self.notes[time]
                if note:
                    buf.write('\t\t\t\tNote '
                        f'Time="{(i%NOTES_PER_PATTERN) * self.note_length}" '
                        f'Value="{note}" Instrument="{self.instrument}"\n')
                else:
                    buf.write('\t\t\t\tNote '
                        f'Time="{(i%NOTES_PER_PATTERN) * self.note_length}" Value="Stop"\n')
        for i in range(args.pattern_count):
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
        lead = randint(0, 2)
        offset = randint(0, 11)
        root = NOTES[offset]
        if args.all_scales:
            scale_name, which_scale = choice(list(SCALES.items()))
        else:
            scale_name, which_scale = choice(list(PENT_SCALES.items()))
        scale_name = f'{root} {scale_name}'
        octave_size = len(which_scale)

        sq1_scale = create_scale(which_scale, args.min_octave+1, args.max_octave, offset)
        sq2_scale = create_scale(which_scale, args.min_octave, args.max_octave-1, offset)
        tri_scale = create_scale(which_scale, args.min_octave, args.tri_max_octave, offset)

        out.write(f'\tSong Name="{song:02d} ({scale_name})" Length="{args.pattern_count}" '
                f'LoopPoint="0" PatternLength="{NOTES_PER_PATTERN}" BarLength="4" NoteLength="{note_length}"\n')

        sq1_track = Track("Square1", args.sq1_repeat_at, sq1_scale, root, f'Lead{lead}', 
                note_length, args.new_note_chance, args.stop_note_chance).generate()
        sq2_track = Track("Square2", args.sq2_repeat_at, sq2_scale, root, f'Lead{lead}',
                note_length, args.new_note_chance, args.stop_note_chance).generate()
        tri_track = Track("Triangle", args.tri_repeat_at, tri_scale, root, 'TriBass',
                note_length, args.tri_new_note_chance, args.stop_note_chance).generate()

        out.write(str(sq1_track))
        out.write(str(sq2_track))
        out.write(str(tri_track))

        # Percussion track
        out.write('\t\tChannel Type="Noise"\n')
        for j in range(0, args.percussion_patterns):
            out.write(f'\t\t\tPattern Name="Pattern {j}"\n')
            for i in range(0, args.pattern_count, 2):
                if random() < 0.5:
                    instr, note = percussion_instrument()
                    out.write(f'\t\t\t\tNote Time="{(i%NOTES_PER_PATTERN) * note_length}" Value="{note}" Instrument="{instr}"\n')
        for i in range(args.pattern_count):
            out.write(f'\t\t\tPatternInstance Time="{i}" Pattern="Pattern {i % args.percussion_patterns}"\n')

    if args.filename:
        out.close()

if __name__ == '__main__':
    args = parse_args()
    main()

