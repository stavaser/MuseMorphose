import miditoolkit
import pickle

def pickle_dump(obj, f):
  pickle.dump(obj, open(f, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

def extract_unique_values(data):
    unique_values = set()

    for key, value in data.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict):
                    for sub_sub_value in sub_value.values():
                        unique_values.update(set(sub_sub_value))
                else:
                    unique_values.update(set(sub_value))
        else:
            unique_values.add(value)

    return unique_values



def create_midi_vocabulary(song_data):
    # Load the MIDI file
    # midi_obj = miditoolkit.midi.parser.MidiFile(midi_file_path)
    
    # Set to store unique MIDI events
    vocabulary = set()

    # print(song_data)
    unique_values = set()
    # print(song_data["notes"])
    unique_values.add("Bar_None")

    for value in song_data["notes"][0]:
        note = song_data["notes"][0][value][0]

        unique_values.add('Note_Pitch_{}'.format(note.pitch))
        unique_values.add('Note_Velocity_{}'.format(note.velocity))
        unique_values.add('Note_Duration_{}'.format(note.end - note.start))
    
    # TODO: chords

    for value in song_data["tempos"][0]:
        unique_values.add('Tempo_{}'.format(value.tempo))

    unique_values.add("EOS_None")

    # enum values
    enum_dict = {value: index for index, value in enumerate(unique_values)}
    # print(len(enum_dict))
    pickle_dump((enum_dict, {}), "../pickles/custom_vocab.pkl")
    
