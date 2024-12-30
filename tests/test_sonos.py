# coding: UTF-8
import json
import time
import unittest
import logging
from time import sleep

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
        self.tst.debug_input_value[self.tst.PIN_I_RINCON] = self.cred["Roam"]  ## ["Buro"]
        # self.tst.debug_input_value[self.tst.PIN_I_RINCON] = self.cred["Wohnzimmer_Fehler"]

        self.tst.on_init()

    def test_encode(self):
        val = self.tst._unencode("&lt;DIDL-Litexmlns:dc=&quot;http://purl.org/dc/elements/1.1/&quot;xmlns:upnp=&quot;urn:schemas-upnp-org:metadata-1-0/upnp/&quot;xmlns:r=&quot;urn:schemas-rinconnetworks-com:metadata-1-0/&quot;xmlns=&quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&quot;&gt;&lt;item id=&quot;S://192.168.143.1/fritz.nas/Kiefer_Gruen/media/Audio/tng_red_alert1.mp3&quot; parentID=&quot;S://192.168.143.1/fritz.nas/Kiefer_Gruen/media/Audio&quot; restricted=&quot;true&quot;&gt;&lt;dc:title&gt;tng_red_alert1.mp3&lt;/dc:title&gt;&lt;upnp:class&gt;object.item.audioItem.musicTrack&lt;/upnp:class&gt;&lt;upnp:albumArtURI&gt;/getaa?u=x-file-cifs%3a%2f%2f192.168.143.1%2ffritz.nas%2fKiefer_Gruen%2fmedia%2fAudio%2ftng_red_alert1.mp3&amp;amp;v=2103&lt;/upnp:albumArtURI&gt;&lt;r:description&gt;//192.168.143.1/fritz.nas/Kiefer_Gruen/media/Audio&lt;/r:description&gt;&lt;desc id=&quot;cdudn&quot; nameSpace=&quot;urn:schemas-rinconnetworks-com:metadata-1-0/&quot;&gt;RINCON_AssociatedZPUDN&lt;/desc&gt;&lt;/item&gt;&lt;/DIDL-Lite&gt;")
        print val

    def test_repeat_mode(self):
        self.tst.set_play_mode_repeat()

    def test_uri(self):
        print("# DEBUG | Entering test_uri")
        path = "192.168.143.1/fritz.nas/Kiefer_Gruen/media/Audio"
        file_name = "ding.mp3"
        uri = "x-file-cifs://{}/{}".format(path, file_name)

        self.tst.play_uri(uri, '')

        ###############

        print("# DEBUG | Leaving test_uri")

    def test_join(self):
        self.tst.join_rincon("RINCON_347E5CF2520201400")

    def test_discovery(self):
        global sonos_system
        for rincon in sonos_system:
            print(sonos_system[rincon].print_device())

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

    def test_radio_wz(self):
        fav = "Bayern 3 Radio"
        self.tst.debug_input_value[self.tst.PIN_I_RINCON] = self.cred["Wohnzimmer_Fehler"]
        self.tst.on_init()

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

    def test_multi(self):
        fav = "Bayern 3 Radio"
        self.tst.debug_input_value[self.tst.PIN_I_RINCON] = self.cred["ROOM1"]
        self.tst.on_init()

        self.tst.debug_input_value[self.tst.PIN_I_SRADIO] = fav
        self.tst.on_input_value(self.tst.PIN_I_SRADIO, fav)

        print("\n\n# Waiting...")
        sleep(20)
        print("# Continue...\n\n")

        self.tst.pause()

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
