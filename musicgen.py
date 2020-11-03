#!/usr/bin/env python3

from random import randint
from sys import argv, stdout
from argparse import ArgumentParser

NOTES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
MINOR = (0, 2, 3, 5, 7, 8, 10)
MINOR_PENTATONIC = (0, 3, 5, 7, 10)
MAJOR = (0, 2, 4, 5, 7, 9, 11)
MAJOR_PENTATONIC = (0, 2, 4, 7, 9)
SCALES = (MAJOR, MINOR, MAJOR_PENTATONIC, MINOR_PENTATONIC)
SCALE_NAMES = ("major", "minor", "major pent", "minor pent")

TEMPLATE = """Project Version="2.2.1" TempoMode="FamiStudio" Name="Untitled" Author="python" Copyright="2020"
	Instrument Name="Lead0"
		Envelope Type="Volume" Length="4" Values="12,10,8,6"
		Envelope Type="DutyCycle" Length="1" Values="0"
	Instrument Name="Lead1"
		Envelope Type="Volume" Length="4" Values="12,10,8,6"
		Envelope Type="DutyCycle" Length="1" Values="1"
	Instrument Name="Lead2"
		Envelope Type="Volume" Length="4" Values="8,12,12,8"
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

NOTES_PER_PATTERN = 16


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('filename', nargs='?', help='The filename to save to. '
            'Output goes to stdout if no file is specified.')
    parser.add_argument('-a', '--all-scales', action='store_true', 
            help='Use all minor/major scales instead of just pentatonic scales')
    parser.add_argument('-p', '--pattern-count', type=int, default=16,
            help="Generate this number of patterns for each song. Default is 16.")
    parser.add_argument('-s', '--songs', type=int, default=24,
            help='The number of songs to create. Default is 24.')
    parser.add_argument('-c', '--max-change', type=int, default=3,
            help='The maximum number of notes to move on the scale when generating '
                'a new note. The default is 3. There is still a 1/16 chance of '
                'jumping to a random note for more variety.')
    parser.add_argument('--min-note-length', type=int, default=7,
            help='The minimum number of frames per note in a song. The default is 7.')
    parser.add_argument('--max-note-length', type=int, default=12,
            help='The maximum number of frames per note in a song. The default is 12.')
    parser.add_argument('--min-octave', type=int, default=1,
            help='The lowest octave to use. The default is 1.')
    parser.add_argument('--max-octave', type=int, default=5,
            help='The highest octave to use. The default is 5.')
    parser.add_argument('--tri-max-octave', type=int, default=4,
            help='The highest octave to use for the triangle wave channel. '
                'The default is 4.')
    return parser.parse_args()

def percussion_instrument():
    instr = ("NoiseBassDrum", "NoiseBassDrum", "NoiseBassDrum", "NoiseBassDrum",
            "NoiseBassDrum", "NoiseHiHat", "NoiseSnare", "NoiseCrash")
    note = ("G2", "G2", "G2", "G2", "G2", "E3", "F4", "F3")
    if randint(0,1):
        return None, None
    idx = randint(0, len(instr)-1)
    return instr[idx], note[idx]

def main():
    if args.tri_max_octave > args.max_octave:
        raise ValueError("Max triangle octave must be lower than or equal to "
                "max octave.")
    note_count = args.pattern_count * NOTES_PER_PATTERN
    if args.filename:
        out = open(args.filename, 'w')
    else:
        out = stdout
    out.write(TEMPLATE)
    for song in range(args.songs):
        note_length = randint(args.min_note_length, args.max_note_length) 
        pattern_length = 16
        lead = randint(0, 2)
        if lead == 3:
            lead = "Pick"
        OFFSET = randint(0, 11)
        scale_idx = randint(0 if args.all_scales else 2,3)
        octave_size = len(SCALES[scale_idx])
        SCALE = []
        for i in range(args.min_octave, args.max_octave):
            for j in SCALES[scale_idx]:
                octave = i + ((j + OFFSET) // 12)
                SCALE.append(f'{NOTES[(j+OFFSET)%12]}{octave}')
        scale_name = SCALE_NAMES[scale_idx]
        note = NOTES[OFFSET]
        out.write(f'\tSong Name="Song {song:02d} ({note[:-1]} {scale_name})" Length="{note_count // pattern_length}" LoopPoint="0" PatternLength="{pattern_length}" BarLength="4" NoteLength="{note_length}"\n')
        out.write('\t\tChannel Type="Square1"\n')
        CURRENT = randint(0, len(SCALE)-1)
        for i in range(note_count):
            note = SCALE[CURRENT]
            if not i % pattern_length:
                out.write(f'\t\t\tPattern Name="Pattern {i//pattern_length}"\n')
            elif randint(0,2): # 1/3 chance of generating a new note
                continue
            if randint(0, 5): # 20% chance of a stop note
                out.write(f'\t\t\t\tNote Time="{(i%pattern_length) * note_length}" Value="{note}" Instrument="Lead{lead}"\n')
            else:
                out.write(f'\t\t\t\tNote Time="{(i%pattern_length) * note_length}" Value="Stop"\n')
            if randint(0,15): # 1/16 chance of jumping to a random note
                CURRENT += randint(-args.max_change, args.max_change)
            else:
                CURRENT = randint(0, len(SCALE)-1)
            CURRENT = min(len(SCALE)-1, max(0, CURRENT))
        for i in range(note_count//pattern_length):
            out.write(f'\t\t\tPatternInstance Time="{i}" Pattern="Pattern {i}"\n')

        out.write('\t\tChannel Type="Square2"\n')
        CURRENT = randint(0, len(SCALE)-1)
        for i in range(note_count):
            note = SCALE[CURRENT]
            if not i % pattern_length:
                out.write(f'\t\t\tPattern Name="Pattern {i//pattern_length}"\n')
            elif randint(0,2): # 1/3 chance of generating a new note
                continue
            if randint(0, 5): # 20% chance of a stop note
                out.write(f'\t\t\t\tNote Time="{(i%pattern_length) * note_length}" Value="{note}" Instrument="Lead{lead}"\n')
            else:
                out.write(f'\t\t\t\tNote Time="{(i%pattern_length) * note_length}" Value="Stop"\n')
            if randint(0,15): # 1/16 chance of jumping to a random note
                CURRENT += randint(-args.max_change, args.max_change)
            else:
                CURRENT = randint(0, len(SCALE)-1)
            CURRENT = min(len(SCALE)-1, max(0, CURRENT))
        for i in range(note_count//pattern_length):
            out.write(f'\t\t\tPatternInstance Time="{i}" Pattern="Pattern {i}"\n')

        # TRIANGLE WAVE CHANNEL
        out.write('\t\tChannel Type="Triangle"\n')
        max_note = len(SCALE)-(1 + (args.max_octave - args.tri_max_octave) * octave_size)
        CURRENT = randint(0, max_note)
        for i in range(note_count):
            note = SCALE[CURRENT]
            if not i % pattern_length:
                out.write(f'\t\t\tPattern Name="Pattern {i//pattern_length}"\n')
            elif randint(0,3): # 1/4 chance of generating a new note
                continue
            if randint(0, 5): # 20% chance of a stop note
                out.write(f'\t\t\t\tNote Time="{(i%pattern_length) * note_length}" Value="{note}" Instrument="TriBass"\n')
            else:
                out.write(f'\t\t\t\tNote Time="{(i%pattern_length) * note_length}" Value="Stop"\n')
            if randint(0,15): # 1/16 chance of jumping to a random note
                CURRENT += randint(-args.max_change, args.max_change)
            else:
                CURRENT = randint(0, max_note)
            CURRENT = min(max_note, max(0, CURRENT))
        for i in range(note_count//pattern_length):
            out.write(f'\t\t\tPatternInstance Time="{i}" Pattern="Pattern {i}"\n')

        out.write('\t\tChannel Type="Noise"\n')
        out.write(f'\t\t\tPattern Name="Pattern 1"\n')
        for i in range(0, note_count//pattern_length, 2):
            instr, note = percussion_instrument()
            if instr:
                out.write(f'\t\t\t\tNote Time="{(i%pattern_length) * note_length}" Value="{note}" Instrument="{instr}"\n')
        for i in range(note_count//pattern_length):
            out.write(f'\t\t\tPatternInstance Time="{i}" Pattern="Pattern 1"\n')

        out.write('\t\tChannel Type="DPCM"\n')

    if args.filename:
        out.close()

if __name__ == '__main__':
    args = parse_args()
    main()

