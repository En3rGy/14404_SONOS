# coding: UTF-8
import json
import time
import unittest
import logging

################################
# get the code
with open('framework_helper.py', 'r') as f1, open('../src/14404_SONOS Speaker (14404).py', 'r') as f2:
    framework_code = f1.read()
    debug_code = f2.read()

exec (framework_code + debug_code)

################################################################################


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        print("\n###setUp")
        logging.basicConfig(level=logging.DEBUG)

        with open("credentials.txt") as f:
            self.cred = json.load(f)

        self.tst = SONOSSpeaker_14404_14404(0)
        self.tst.debugging = True
        self.tst.debug_input_value[self.tst.PIN_I_RINCON] = self.cred["ROOM1"]

        self.tst.on_init()

    def test_discovery(self):
        global sonos_system
        for rincon in sonos_system:
            print str(sonos_system[rincon])

    def test_init_and_discovery(self):
        self.assertTrue(self.tst.speaker.rincon != str())

        self.tst = SONOSSpeaker_14404_14404(0)
        self.tst.debug_input_value[self.tst.PIN_I_RINCON] = "No Name"
        self.tst.on_init()
        self.assertTrue(self.tst.speaker.rincon == str())

    def test_two_instances(self):
        self.assertTrue(self.tst.speaker.rincon != str())

        tst2 = SONOSSpeaker_14404_14404(0)
        tst2.debug_input_value[self.tst.PIN_I_ROOM_NAME] = self.cred["ROOM2"]
        tst2.on_init()
        self.assertTrue(tst2.speaker.rincon != str())

    def test_radio(self):
        fav = "Bayern 3 Radio"
        self.tst.debug_input_value[self.tst.PIN_I_SRADIO] = fav
        self.tst.on_input_value(self.tst.PIN_I_SRADIO, fav)
        self.assertEqual(self.tst.debug_output_value[self.tst.PIN_O_OUT], 600)

    def test_nas_song(self):
        fav = "In My Mind"
        # fav = "God Rest Ye Merry Gentlemen"
        self.tst.debug_input_value[self.tst.PIN_I_SPLAYLIST] = fav
        self.tst.on_input_value(self.tst.PIN_I_SPLAYLIST, fav)
        self.assertEqual(self.tst.debug_output_value[self.tst.PIN_O_OUT], 1400)

    def test_volume(self):
        self.tst.on_input_value(self.tst.PIN_I_NVOLUME, 5)
        self.assertEqual(self.tst.debug_output_value[self.tst.PIN_O_OUT], 200)

    def test_pause(self):
        self.tst.pause()
        self.assertEqual(self.tst.debug_output_value[self.tst.PIN_O_OUT], 200)


if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
