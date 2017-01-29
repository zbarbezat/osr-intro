import argparse
import glob
from joblib import Parallel, delayed
import json
import os
import pretty_midi

"""Compute statistics over MIDI files.

Usage
-------
filename : str
	Path ot a midi file on disk.
Returns
--------
counts : dict
	Pitch counts over the file, keyed by pitch class.
Usage
--------
# Run with default parameters
$ python midi_tools.py data/*.mid stats.json

# Run with full verbosity
$ python midi_tools.py data/*.mid stats.json --verbosity 50
"""


def compute_pitch_histogram(filename):
	"""Compute weighted pitch counts over a MIDI file.

	Parameters
	----------
	filename : str
		Path to a midi file on disk.

	Returns
	----------
	counts : dict
		Pitch counts over the file, keyed by pitch class.
	"""
	midi = pretty_midi.PrettyMIDI(filename)
	pitch_counts = {pc: 0 for pc in range(12)}
	name = os.path.split(filename)[-1]
	try:
		midi = pretty_midi.PrettyMIDI(filename)
		for inst in midi.instruments:
			if inst.is_drum:
				continue
			for note in inst.notes:
				pc = note.pitch % 12
				pitch_counts[pc] += (note.end - note.start)

	except IOError as derp:
		print("woah buddy, {} died: {}".format(name, derp))

	finally: 
		return {'name': name,
			'pitches': pitch_counts}

def process_many(filenames, n_jobs=-2, verbose=0):
	pool = Parallel(n_jobs=n_jobs, verbose=verbose)
	fx = delayed(compute_pitch_histogram)
	return pool(fx(fn) for fn in filenames)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filepattern", type=str,
        help="Filepattern for finding MIDI files, e.g. 'data/*.midi")
    parser.add_argument(
    	"output_file", type=str,
    	help="Output file for writing results e.g. 'data.json'")
    parser.add_argument(
    	"--n_jobs", metavar='n_jobs', type=int, default=-2,
    	help="number of CPUs to use for processing.")
    parser.add_argument(
    	"--verbose", metavar='verbose', type=int, default=-0,
    	help="Verbosity level for writing outputs.")

    args = parser.parse_args()
    filenames = glob.glob(args.filepattern)
    results = process_many(filenames, args.n_jobs, args.verbose)
    with open(args.output_file, 'w') as fp:
    	json.dump(results, fp, indent=2)
