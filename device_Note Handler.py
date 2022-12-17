# name=Note Handler
# receiveFrom=Shift Handler
# url=https://github.com/TheNathanSpace/FL-Studio-Key-Mapper

import midi
import ui

scales_dict = {}

all_notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

sharps_flats_map = {
    "F#": "Gb",
    "C#": "Db",
    "G#": "Ab",
    "D#": "Eb",
    "A#": "Bb",
    "E#": "F",
}
flats_sharps_map = {v: k for k, v in sharps_flats_map.items()}

id_to_name_dict = {}
name_to_id_dict = {}

shift_is_on = False

current_key = "C"


def index_of(list_in, item):
    counter = 0
    for i in list_in:
        if item == i:
            return counter
        counter += 1
    return -1


def read_scales_file():
    input_file = \
        """
        C	D	E	F	G	A	B
        G	A	B	C	D	E	F#
        D	E	F#	G	A	B	C#
        A	B	C#	D	E	F#	G#
        E	F#	G#	A	B	C#	D#
        B	C#	D#	E	F#	G#	A#
        F#	G#	A#	B	C#	D#	E#
        Db	Eb	F	Gb	Ab	Bb	C
        Ab	Bb	C	Db	Eb	F	G
        Eb	F	G	Ab	Bb	C	D
        Bb	C	D	Eb	F	G	A
        F	G	A	Bb	C	D	E
        """
    lines = input_file.split("\n")
    for line in lines:
        # Skip comments and blank lines
        if "#" in line:
            continue
        if line == "\n":
            continue

        line = line.replace(" ", "")
        split_line = line.split("\t")
        root_note = split_line[0]
        scales_dict[root_note] = []
        for note in split_line:
            note = note.replace("\n", "")
            scales_dict[root_note].append(note)


def map_note_ids():
    note_index = 0
    octave = 0
    for i in range(0, 128):
        note_letter = all_notes[note_index]
        id_to_name_dict[i] = note_letter + str(octave)

        note_index += 1
        if note_index == 12:
            note_index = 0

        if all_notes[note_index] == "C":
            octave += 1

    global name_to_id_dict
    name_to_id_dict = {v: k for k, v in id_to_name_dict.items()}


def get_no_octave(note_id):
    no_octave = ''.join([i for i in id_to_name_dict[note_id] if not i.isdigit()])
    return no_octave


def get_c_index(note_id):
    return index_of(scales_dict["C"], get_no_octave(note_id))


def get_octave(note_id):
    just_octave = ''.join([i for i in id_to_name_dict[note_id] if i.isdigit()])
    return just_octave


def OnMidiMsg(event):
    event.handled = False

    # print("MIDI STATUS", event.midiId, "|", "MIDI DATA1", event.data1, "|",
    #       "MIDI DATA2", event.data2, "|", "MIDI status", event.status, "|",
    #       "Channel", (event.midiChan + 1), event.sysex, "|", "Handled", event.handled)  # Prints MIDI data from pads, knobs and other buttons. Useful for debugging.

    if event.midiId == midi.MIDI_NOTEON:
        if event.pmeFlags & midi.PME_System != 0:
            # print("\nBefore: " + id_to_name_dict[event.data1] + " on channel " + str(event.midiChan))
            global current_key
            # Only perform this on key down, not up
            if shift_is_on and event.data2 != 0:
                change_to = get_no_octave(event.data1)

                if change_to not in scales_dict:
                    # Convert sharp to flat
                    change_to = sharps_flats_map[change_to]

                    if change_to not in scales_dict:
                        message = "Couldn't change key signature to " + change_to
                        ui.setHintMsg(message)
                        print(message)
                        return

                current_key = change_to
                message = "Changed mapped key signature to: " + current_key
                ui.setHintMsg(message)
                print(message)
                event.handled = True
                return

            if current_key != "C" and event.midiChan == 0:
                # Ignore sharps/flats while mapping
                if "#" in id_to_name_dict[event.data1] or "b" in id_to_name_dict[event.data1]:
                    event.handled = True
                    return

                # Get position of original note in scale
                c_index = get_c_index(event.data1)

                # Get translated note from new key
                translated_key = scales_dict[current_key][c_index]
                octave = get_octave(event.data1)

                # Fix octave if note is late enough
                for note in scales_dict[current_key][:c_index + 1]:
                    if note == "C":
                        octave = int(octave) + 1
                        octave = str(octave)
                        break

                # Get note ID
                translated_key_with_octave = translated_key + octave
                if translated_key_with_octave in name_to_id_dict:
                    translated_id = name_to_id_dict[translated_key_with_octave]
                else:
                    # Convert flat to sharp if necessary
                    translated_id = name_to_id_dict[flats_sharps_map[translated_key] + octave]

                # Modify event note
                event.data1 = translated_id
                # print("After: " + id_to_name_dict[event.data1] + " on channel " + str(event.midiChan))


def OnSysEx(event):
    received_message = int.from_bytes(bytes = event.sysex, byteorder = 'big')

    global shift_is_on
    if received_message == 18:
        shift_is_on = True
    elif received_message == 17:
        shift_is_on = False


if __name__ == "__main__":
    read_scales_file()
    map_note_ids()
    print("Initialized note handler\n")