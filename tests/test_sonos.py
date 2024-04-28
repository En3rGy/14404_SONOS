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
        self.tst.debug_input_value[self.tst.PIN_I_SSPEAKERIP] = self.cred["IP"]
        self.tst.debug_input_value[self.tst.PIN_I_NSPEAKERPORT] = "1400"

        self.tst.on_init()

    def test_discovery(self):
        self.tst.discovery()
        self.assertIsNot(self.tst.rincon, str())

    def test_volume(self):
        self.tst.on_input_value(self.tst.PIN_I_NVOLUME, 5)
        self.assertTrue(self.tst.debug_output_value[self.tst.PIN_O_OUT])

    def test_playlist(self):
        self.tst.on_input_value(self.tst.PIN_I_SPLAYLIST, "Bayern 3 Radio")
        self.assertTrue(self.tst.debug_output_value[self.tst.PIN_O_OUT])


if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
