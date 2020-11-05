# famistudio-musicgen
Generates Famistudio Text format files with procedurally generated music.


## Example Tracks

There are some example tracks from this software on [Soundcloud](https://soundcloud.com/tjmcgrew/sets/chiptunesbot)

```text
    usage: musicgen.py [-h] [-a] [-p PATTERN_COUNT] [-s SONGS] [-c MAX_CHANGE]
                       [--min-note-length MIN_NOTE_LENGTH]
                       [--max-note-length MAX_NOTE_LENGTH]
                       [--min-octave MIN_OCTAVE] [--max-octave MAX_OCTAVE]
                       [--tri-max-octave TRI_MAX_OCTAVE]
                       [--new-note-chance NEW_NOTE_CHANCE]
                       [--tri-new-note-chance TRI_NEW_NOTE_CHANCE]
                       [--stop-note-chance STOP_NOTE_CHANCE] [--scale SCALE]
                       [filename]

    positional arguments:
      filename              The filename to save to. Output goes to stdout if no
                            file is specified.

    optional arguments:
      -h, --help            show this help message and exit
      -a, --all-scales      Use all minor/major scales instead of just pentatonic
                            scales
      -p PATTERN_COUNT, --pattern-count PATTERN_COUNT
                            Generate this number of patterns for each song.
                            Default is 16.
      -s SONGS, --songs SONGS
                            The number of songs to create. Default is 24.
      -c MAX_CHANGE, --max-change MAX_CHANGE
                            The maximum number of notes to move on the scale when
                            generating a new note. The default is 3. There is
                            still a chance of jumping to a random note for more
                            variety.
      --min-note-length MIN_NOTE_LENGTH
                            The minimum number of frames per note in a song. The
                            default is 8.
      --max-note-length MAX_NOTE_LENGTH
                            The maximum number of frames per note in a song. The
                            default is 12.
      --min-octave MIN_OCTAVE
                            The lowest octave to use. The default is 1.
      --max-octave MAX_OCTAVE
                            The highest octave to use. The default is 4.
      --tri-max-octave TRI_MAX_OCTAVE
                            The highest octave to use for the triangle wave
                            channel. The default is 4.
      --new-note-chance NEW_NOTE_CHANCE
                            The chance to generate a new note at each beat.
                            Default is 0.4
      --tri-new-note-chance TRI_NEW_NOTE_CHANCE
                            The chance to generate a new note at each beat on the
                            triangle wave channel. Default is 0.3.
      --stop-note-chance STOP_NOTE_CHANCE
                            The chance to generate a stop note when creating a new
                            note. Default is 0.2
      --scale SCALE         Print the notes in a scale to the command line and
                            exit. e.g. "C major" or "F# minor".
```
