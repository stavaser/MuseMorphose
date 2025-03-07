import os
import copy
import numpy as np
import multiprocessing as mp

import miditoolkit
from miditoolkit.midi import parser as mid_parser
from miditoolkit.pianoroll import parser as pr_parser
from miditoolkit.midi.containers import Marker, Instrument, TempoChange

from chorder import Dechorder


num2pitch = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B",
}


def traverse_dir(
    root_dir,
    extension=("mid", "MID", "midi"),
    amount=None,
    str_=None,
    is_pure=False,
    verbose=False,
    is_sort=False,
    is_ext=True,
):
    if verbose:
        print("[*] Scanning...")
    file_list = []
    cnt = 0
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(extension):
                if (amount is not None) and (cnt == amount):
                    break
                if str_ is not None:
                    if str_ not in file:
                        continue
                mix_path = os.path.join(root, file)
                pure_path = mix_path[len(root_dir) + 1 :] if is_pure else mix_path
                if not is_ext:
                    ext = pure_path.split(".")[-1]
                    pure_path = pure_path[: -(len(ext) + 1)]
                if verbose:
                    print(pure_path)
                file_list.append(pure_path)
                cnt += 1
    if verbose:
        print("Total: %d files" % len(file_list))
        print("Done!!!")
    if is_sort:
        file_list.sort()
    return file_list


def proc_one(path_infile, path_outfile):
    print("----")
    print(" >", path_infile)
    print(" >", path_outfile)

    # load
    midi_obj = miditoolkit.midi.parser.MidiFile(path_infile)
    midi_obj_out = copy.deepcopy(midi_obj)
    notes = midi_obj.instruments[0].notes
    notes = sorted(notes, key=lambda x: (x.start, x.pitch))

    # --- chord --- #
    # exctract chord
    chords = Dechorder.dechord(midi_obj)
    markers = []
    for cidx, chord in enumerate(chords):
        if chord.is_complete():
            chord_text = (
                num2pitch[chord.root_pc]
                + "_"
                + chord.quality
                + "_"
                + num2pitch[chord.bass_pc]
            )
        else:
            chord_text = "N_N_N"
        markers.append(Marker(time=int(cidx * 480), text=chord_text))

    # dedup
    prev_chord = None
    dedup_chords = []
    for m in markers:
        if m.text != prev_chord:
            prev_chord = m.text
            dedup_chords.append(m)

    # --- global properties --- #
    # global tempo
    tempos = [b.tempo for b in midi_obj.tempo_changes][:40]
    tempo_median = np.median(tempos)
    global_bpm = int(tempo_median)
    print(" > [global] bpm:", global_bpm)

    # === save === #
    # mkdir
    fn = os.path.basename(path_outfile)
    os.makedirs(path_outfile[: -len(fn)], exist_ok=True)

    # markers
    midi_obj_out.markers = dedup_chords
    midi_obj_out.markers.insert(
        0, Marker(text="global_bpm_" + str(int(global_bpm)), time=0)
    )

    # save
    midi_obj_out.instruments[0].name = "piano"
    midi_obj_out.dump(path_outfile)


if __name__ == "__main__":
    # paths
    path_indir = "./midi_synchronized"
    path_outdir = "./midi_analyzed"
    os.makedirs(path_outdir, exist_ok=True)

    # list files
    midifiles = traverse_dir(path_indir, is_pure=True, is_sort=True)
    n_files = len(midifiles)
    print("num fiels:", n_files)

    # collect
    data = []
    for fidx in range(n_files):
        path_midi = midifiles[fidx]
        print("{}/{}".format(fidx, n_files))

        # paths
        path_infile = os.path.join(path_indir, path_midi)
        path_outfile = os.path.join(path_outdir, path_midi)

        # append
        data.append([path_infile, path_outfile])

    # run, multi-thread
    pool = mp.Pool()
    pool.starmap(proc_one, data)
