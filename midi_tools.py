from joblib import Parallel, delayed
import pretty_midi



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

	for inst in midi.instruments:
		if inst.is_drum:
			continue
		for note in inst.notes:
			pc = note.pitch % 12
			pitch_counts[pc] += (note.end - note.start)
		return pitch_counts

def process_many(filenames, n_jobs=-2, verbose=0):
	pool = Parallel(n_jobs=n_jobs, verbose=verbose)
	fx = delayed(compute_pitch_histogram)
	return pool(fx(fn) for fn in filenames)