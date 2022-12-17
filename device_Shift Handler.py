# name=Shift Handler
# url=https://github.com/TheNathanSpace/FL-Studio-Key-Mapper

import device
import midi
import transport

shift_DATA1 = 108
record_DATA1 = 117
play_DATA1 = 115


def OnMidiMsg(event):
    event.handled = False

    # print("MIDI STATUS", event.midiId, "|", "MIDI DATA1", event.data1, "|",
    #       "MIDI DATA2", event.data2, "|", "MIDI status", event.status, "|",
    #       "Channel", (event.midiChan + 1), event.sysex, "|", "Handled", event.handled)  # Prints MIDI data from pads, knobs and other buttons. Useful for debugging.

    if event.midiId == midi.MIDI_CONTROLCHANGE:
        if event.data1 == shift_DATA1:
            # Device 0 = port 170 = Note Handler
            if event.data2:
                device.dispatch(0, 0xF0, bytes([18]))
            else:
                device.dispatch(0, 0xF0, bytes([17]))
            return
        elif event.data1 == record_DATA1:
            if event.data2:
                transport.record()
            return
        elif event.data1 == play_DATA1:
            if event.data2:
                if transport.isPlaying():
                    transport.stop()
                else:
                    transport.start()
            return


if __name__ == "__main__":
    print("Initialized shift handler\n")