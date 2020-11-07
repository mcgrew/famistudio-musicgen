# famistudio-musicgen
Generates Famistudio Text format files with procedurally generated music.


## Example Tracks

There are some example tracks from this software on [Soundcloud](https://soundcloud.com/tjmcgrew/sets/chiptunesbot)

```text
    usage: musicgen.py [-h] [-a] [--pattern-count COUNT] [-s SONGS]
                       [-c MAX_CHANGE] [--min-note-length FRAMES]
                       [--max-note-length FRAMES] [--min-octave OCTAVE]
                       [--max-octave OCTAVE] [--tri-max-octave OCTAVE]
                       [--sq1-repeat-at PATTERN] [--sq2-repeat-at PATTERN]
                       [--tri-repeat-at PATTERN]
                       [--percussion-patterns PERCUSSION_PATTERNS] [-n CHANCE]
                       [-t CHANCE] [-p CHANCE] [--scale SCALE]
                       [filename]

    positional arguments:
      filename              The filename to save to. Output goes to stdout if no
                            file is specified.

    optional arguments:
      -h, --help            show this help message and exit
      -a, --all-scales      Use all scales instead of just pentatonic scales
      --pattern-count COUNT
                            Generate this number of patterns for each song.
                            Default is 16.
      -s SONGS, --songs SONGS
                            The number of songs to create. Default is 10.
      -c MAX_CHANGE, --max-change MAX_CHANGE
                            The maximum number of notes to move on the scale when
                            generating a new note. The default is 3. There is
                            still a chance of jumping to a random note for more
                            variety.
      --min-note-length FRAMES
                            The minimum number of frames per note in a song. The
                            default is 8.
      --max-note-length FRAMES
                            The maximum number of frames per note in a song. The
                            default is 12.
      --min-octave OCTAVE   The lowest octave to use. The default is 1.
      --max-octave OCTAVE   The highest octave to use. The default is 4.
      --tri-max-octave OCTAVE
                            The highest octave to use for the triangle wave
                            channel. The default is 4.
      --sq1-repeat-at PATTERN
                            Forces square wave track 1 to start repeating after
                            the given number of patterns. This works best if it is
                            a factor of pattern count. The default is 0 (do not
                            repeat).
      --sq2-repeat-at PATTERN
                            Forces square wave track 1 to start repeating after
                            the given number of patterns. This works best if it is
                            a factor of pattern count. The default is 0 (do not
                            repeat).
      --tri-repeat-at PATTERN
                            Forces triangle wave track to start repeating after
                            the given number of patterns. This works best if it is
                            a factor of pattern count. The default is 0 (do not
                            repeat).
      --percussion-patterns PERCUSSION_PATTERNS
                            The number of percussion patterns to generate. This
                            works best if it is a factor of pattern count. The
                            default is 1.
      -n CHANCE, --new-note-chance CHANCE
                            The chance to generate a new note at each beat.
                            Default is 0.35
      -t CHANCE, --tri-new-note-chance CHANCE
                            The chance to generate a new note at each beat on the
                            triangle wave channel. Default is 0.3.
      -p CHANCE, --stop-note-chance CHANCE
                            The chance to generate a stop note when creating a new
                            note. Default is 0.2
      --scale SCALE         Print the notes in a scale to the command line and
                            exit. e.g. "C major" or "F# minor".
```
