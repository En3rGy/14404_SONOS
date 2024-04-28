# coding: UTF-8
import httplib
import socket
import urllib2
import xml.etree.ElementTree as ET
import urlparse

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class SONOSSpeaker_14404_14404(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "hsl20_3_SonosSpeaker")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE, ())
        self.PIN_I_SSPEAKERIP = 1
        self.PIN_I_NSPEAKERPORT = 2
        self.PIN_I_NVOLUME = 3
        self.PIN_I_BPLAY = 4
        self.PIN_I_BPAUSE = 5
        self.PIN_I_BPREVIOUS = 6
        self.PIN_I_BNEXT = 7
        self.PIN_I_SPLAYLIST = 8
        self.PIN_I_SRADIO = 9
        self.PIN_I_SJOINRINCON = 10
        self.PIN_O_OUT = 1

    ########################################################################################################
    #### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
    ###################################################################################################!!!##

        self.location = str()
        self.rincon = str()

    def set_output_value_sbc(self, pin, val):
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print ("# SBC: pin " + str(pin) + " <- data not send / " + str(val).decode("utf-8"))
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val

    def log_msg(self, text):
        self.DEBUG.add_message("14403: {}".format(text))

    def log_data(self, key, value):
        self.DEBUG.set_value("14403 {}".format(key), str(value))

    def hex2int(msg):
        """

        :param msg: hex number (e.g. 0x11)
        :type msg: str
        :return: Int representation of hex value
        :rtype: int
        """
        if not msg:
            return 0

        msg = bytearray(msg)
        val = 0
        val = val | msg[0]
        for byte in msg[1:]:
            val = val << 8
            val = val | byte

        return int(val)

    def discovery(self):
        """
        Function to automatically discover the Hue bridge IP.
        Returns a tuple of status message and bridge IP.

        :type host_ip: str
        :param host_ip: IP of machine, hosting the logic module.
        :rtype: str, str
        :return: error message, ip
        """

        host_ip = self.FRAMEWORK.get_homeserver_private_ip()
        MCAST_PORT = 1900
        MCAST_GRP = ('239.255.255.250', MCAST_PORT)

        message_header = "M-SEARCH * HTTP/1.1\r\n";
        message_host = "HOST: 239.255.255.250:1900\r\n";
        message_man = "MAN: \"ssdp:discover\"\r\n";
        message_mx = "MX: 8\r\n";
        message_st = "ST: urn:schemas-upnp-org:device:ZonePlayer:1\r\n";

        msg = message_header + message_host + message_man + message_mx + message_st + "\r\n"

        # configure socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 8)
        sock.settimeout(5)
        sock.bind((host_ip, 0))  # host_ip = self.FRAMEWORK.get_homeserver_private_ip()

        # send data
        bytes_send = sock.sendto(msg, MCAST_GRP)
        if bytes_send != len(msg):
            self.log_msg("Something wrong here, send bytes not equal provided bytes")

        while True:
            try:
                response = sock.recv(1024)
                # print(response)

                if "SONOS" in response.upper():
                    lines = response.split('\n')
                    for line in lines:
                        if line.startswith('LOCATION:'):
                            location = line.split(': ')[1].strip()
                            if urlparse.urlparse(location).hostname == self._get_input_value(self.PIN_I_SSPEAKERIP):
                                self.location = location
                            else:
                                continue

                        if line.startswith('USN:'):
                            usn = line.split(': ')[1].strip()
                            self.rincon = usn.split(':')[1].strip()
                            break  # for-loop

                    if self.location:
                        break  # while loop

            except socket.timeout:
                break

        sock.close()
        self.log_data("RINCON", self.rincon)
        self.log_data("Location", self.location)

    def http_put(self, api_path, api_action, payload):
        http_client = None

        ip = self._get_input_value(self.PIN_I_SSPEAKERIP)
        port = self._get_input_value(self.PIN_I_NSPEAKERPORT)
        try:
            headers = {"CONNECTION": "close",
                       "HOST": "{}:{}".format(ip, port),
                       "CONTENT-LENGTH": str(len(payload)),
                       "Content-type": 'text/xml; charset="utf-8"',
                       "SOAPACTION": api_action}
            http_client = httplib.HTTPConnection(ip, int(port), timeout=5)
            http_client.request("POST", api_path, payload, headers)
            response = http_client.getresponse()
            status = response.status
            print(response.read())
            # self.DEBUG.set_value('10034 response', response.read())
            self.log_data('status', status)
            if str(status) != '200':
                return False
            else:
                return True
        except Exception as e:
            self.log_msg(str(e))
            # data = {'status':500,'auth':'failed'}
            return False
        finally:
            if http_client:
                http_client.close()

    def set_mute(self, do_set_mute):
        api_action = '"urn:schemas-upnp-org:service:RenderingControl:1#SetMute"'
        data = get_data_str('<u:SetMute xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">'
                            '<InstanceID>0</InstanceID><Channel>Master</Channel><DesiredMute>{}</DesiredMute>'
                            '</u:SetMute>'.format(int(do_set_mute)))

        return self.http_put("/MediaRenderer/AVTransport/Control", api_action, data)

    def clear_queue(self):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#RemoveAllTracksFromQueue"'
        data = get_data_str('<u:RemoveAllTracksFromQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID></u:RemoveAllTracksFromQueue>')

        return self.http_put("/MediaRenderer/AVTransport/Control", api_action, data)

    def select_fst_track(self, ):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Seek"'
        data = get_data_str('<u:Seek xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID><Unit>TRACK_NR</Unit><Target>1</Target></u:Seek>')

        return self.http_put("/MediaRenderer/AVTransport/Control", api_action, data)

    def set_playlist_active(self, ):
        if self.rincon is str():
            self.discovery()

        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'
        data = get_data_str('<u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID><CurrentURI>x-rincon-queue:{}'
                            '</CurrentURI><CurrentURIMetaData></CurrentURIMetaData>'
                            '</u:SetAVTransportURI>'.format(self.rincon))

        return self.http_put("/MediaRenderer/AVTransport/Control", api_action, data)

    # Playlist Children
    def set_playlist(self, data):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#AddURIToQueue"'
        str_list = str.split(data, "*")

        if len(str_list) != 2:
            return False

        # <u:AddURIToQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
        #   <InstanceID>0</InstanceID>
        #   <EnqueuedURI>x-rincon-playlist:RINCON_949F3E71146601400#A:GENRE/Children&apos;s</EnqueuedURI>
        #   <EnqueuedURIMetaData>???
        #   </EnqueuedURIMetaData>
        #   <DesiredFirstTrackNumberEnqueued>1</DesiredFirstTrackNumberEnqueued>
        #   <EnqueueAsNext>1</EnqueueAsNext>
        #   </u:AddURIToQueue>'

        data2 = get_data_str('<u:AddURIToQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                             '<InstanceID>0</InstanceID><EnqueuedURI>{}</EnqueuedURI>'
                             '<EnqueuedURIMetaData>{}</EnqueuedURIMetaData>'
                             '<DesiredFirstTrackNumberEnqueued>1</DesiredFirstTrackNumberEnqueued>'
                             '<EnqueueAsNext>1</EnqueueAsNext>'
                             '</u:AddURIToQueue>'.format(str_list[0], str_list[1]))

        return self.http_put("/MediaRenderer/AVTransport/Control", api_action, data2)

    def set_play_mode_shuffle_no_repeat(self, ):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#SetPlayMode"'
        data = get_data_str('<u:SetPlayMode xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID><NewPlayMode>SHUFFLE_NOREPEAT</NewPlayMode>'
                            '</u:SetPlayMode>')

        return self.http_put("/MediaRenderer/AVTransport/Control", api_action, data)

    def play(self):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Play"'
        data = get_data_str('<u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID><Speed>1</Speed></u:Play>')

        return self.http_put("/MediaRenderer/AVTransport/Control", api_action, data)

    def play_next(self):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Next"'
        data = get_data_str('<u:Next xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID></u:Next>')

        return self.http_put("/MediaRenderer/AVTransport/Control", api_action, data)

    def play_previous(self):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Previous"'
        data = get_data_str('<u:Previous xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID></u:Previous>')

        return self.http_put("/MediaRenderer/AVTransport/Control", api_action, data)

    def pause(self):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Pause"'
        data = get_data_str('<u:Pause xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID></u:Pause>')

        return self.http_put("/MediaRenderer/AVTransport/Control", api_action, data)

    def set_volume(self, volume):
        api_action = '"urn:schemas-upnp-org:service:RenderingControl:1#SetVolume"'
        data = get_data_str('<u:SetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">'
                            '<InstanceID>0</InstanceID><Channel>Master</Channel><DesiredVolume>{}'
                            '</DesiredVolume></u:SetVolume>'.format(volume))

        # return self.http_put("/MediaRenderer/RenderingControl/Control HTTP/1.1", api_action, data)
        return self.http_put("/MediaRenderer/RenderingControl/Control", api_action, data)

    def play_radio(self, data):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'
        str_list = str.split(data, "*")

        if len(str_list) != 2:
            return False

        data2 = get_data_str('<u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                             '<InstanceID>0</InstanceID><CurrentURI>{}</CurrentURI>'
                             '<CurrentURIMetaData>{}</CurrentURIMetaData>'
                             '</u:SetAVTransportURI>'.format(str_list[0], str_list[1]))

        ret = self.http_put("/MediaRenderer/AVTransport/Control", api_action, data2)

        if ret:
            return self.play()

    def play_playlist(self, data):
        ret = self.clear_queue()
        if not ret:
            return False

        ret = self.set_playlist(data)
        if not ret:
            return False

        ret = self.set_playlist_active()
        if not ret:
            return False

        ret = self.set_play_mode_shuffle_no_repeat()
        if not ret:
            return False

        ret = self.select_fst_track()
        if not ret:
            return False

        return self.play()

    def join_rincon(self, rincon):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'
        data = get_data_str('<u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID><CurrentURI>x-rincon:RINCON_{}</CurrentURI>'
                            '<CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI>'.format(rincon))

        return self.http_put("/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

    def on_input_value(self, index, value):

        ip = self._get_input_value(self.PIN_I_SSPEAKERIP)
        port = self._get_input_value(self.PIN_I_NSPEAKERPORT)
        res = False

        if (ip == "") or (port == 0):
            self._set_output_value(self.PIN_O_SOUT, "IP or Port not set.")
            return

        if (index == self.PIN_I_BNEXT) and (bool(value)):
            res = self.play_next()

        elif (index == self.PIN_I_BPAUSE) and (bool(value)):
            res = self.pause()

        elif (index == self.PIN_I_BPLAY) and (bool(value)):
            res = self.play()

        elif (index == self.PIN_I_BPREVIOUS) and (bool(value)):
            res = self.play_previous()

        elif (index == self.PIN_I_SPLAYLIST) and (bool(value)):
            res = self.play_playlist(self._get_input_value(self.PIN_I_SPLAYLIST))

        elif (index == self.PIN_I_SRADIO) and (bool(value)):
            res = self.play_radio(self._get_input_value(self.PIN_I_SRADIO))

        elif index == self.PIN_I_NVOLUME:
            res = self.set_volume(value)

        elif index == self.PIN_I_SJOINRINCON:
            res = self.join_rincon(self._get_input_value(self.PIN_I_SJOINRINCON))

        self._set_output_value(self.PIN_O_OUT, res)
        self.log_data("index/success", "{}/{}".format(index, res))


def get_data_str(command):
    data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" ' \
           's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>' \
           '{}</s:Body></s:Envelope>'.format(command)
    return data
