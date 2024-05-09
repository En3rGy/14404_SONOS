# coding: UTF-8
import httplib
import socket
import urllib2
import xml.etree.ElementTree as ET
import urlparse
import threading
import re

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class SONOSSpeaker_14404_14404(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "14404_SonosSpeaker")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_RINCON=1
        self.PIN_I_NVOLUME=2
        self.PIN_I_PLAY=3
        self.PIN_I_BPREVIOUS=4
        self.PIN_I_BNEXT=5
        self.PIN_I_SPLAYLIST=6
        self.PIN_I_SRADIO=7
        self.PIN_I_SJOINRINCON=8
        self.PIN_O_OUT=1

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

        self.speaker = SonosPlayer()

    def set_output_value_sbc(self, pin, val):
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print ("# SBC: pin " + str(pin) + " <- data not send / " + str(val).decode("utf-8"))
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val

    def log_msg(self, text):
        self.DEBUG.add_message("14403 | {}: {}".format(self._get_input_value(self.PIN_I_RINCON), text))

    def log_data(self, key, value):
        self.DEBUG.set_value("14403 | {}: {}".format(self._get_input_value(self.PIN_I_RINCON), key), str(value))

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
        print("Entering discovery...")

        host_ip = self.FRAMEWORK.get_homeserver_private_ip()
        MCAST_PORT = 1900
        MCAST_GRP = ('239.255.255.250', MCAST_PORT)

        message_header = "M-SEARCH * HTTP/1.1\r\n"
        message_host = "HOST: 239.255.255.250:1900\r\n"
        message_man = "MAN: \"ssdp:discover\"\r\n"
        message_mx = "MX: 8\r\n"
        message_st = "ST: urn:schemas-upnp-org:device:ZonePlayer:1\r\n"

        msg = message_header + message_host + message_man + message_mx + message_st + "\r\n"

        # configure socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 8)
        sock.settimeout(5)
        sock.bind((host_ip, 0))  # host_ip = self.FRAMEWORK.get_homeserver_private_ip()

        # send data
        bytes_send = sock.sendto(msg, MCAST_GRP)
        if bytes_send != len(msg):
            raise BaseException("discovery |Something wrong here, send bytes not equal provided bytes")

        global sonos_system
        sonos_system = []
        while True:
            try:
                response = sock.recv(1024)

                if "SONOS" in response.upper():
                    player = SonosPlayer()
                    player.rincon = re.search("USN: uuid:(.*?):", response, re.MULTILINE).group(1)
                    player.location = re.search("LOCATION: (.*?)\n", response, re.MULTILINE).group(1)
                    player.ip = urlparse.urlparse(player.location).hostname
                    player.port = urlparse.urlparse(player.location).port

                    player.get_data()

                    sonos_system.append(player)

            except socket.timeout:
                break

        sock.close()

        self.log_msg("Discovered {} SONOS devices: {}".format(len(sonos_system),
                                                              ", ".join(speaker.name for speaker in sonos_system)))

    def get_speaker_data(self):
        """
        Gets the metadata for the current player

        :return:
        """
        self._get_speaker_data()

        if self.speaker.rincon == str():
            self.discovery()
            self._get_speaker_data()
            if self.speaker.rincon == str():
                raise BaseException("get_speaker_data | Speaker not found. Is ist offline?")

        self.log_data("RINCON", self.speaker.rincon)
        self.log_data("Location", self.speaker.location)

    def _get_speaker_data(self):
        """
        Gets the metadata for the current player

        :return:
        """
        global sonos_system
        if 'sonos_system' not in globals():
            self.discovery()

        for speaker in sonos_system:
            if speaker.rincon == self._get_input_value(self.PIN_I_RINCON):
                self.speaker = speaker
                self.speaker.get_data()
                break
            else:
                continue

    def _http_put(self, api_path, api_action, payload):
        """
        Perform an HTTP PUT request.

        :param api_path: The API path for the request.
        :type api_path: str
        :param api_action: The action to perform.
        :type api_action: str
        :param payload: The payload to send with the request.
        :type payload: str
        :return: The response data from the server. str() in case of error.
        :rtype: str
        """
        print("Entering http_put...")
        http_client = None

        ip = self.speaker.ip
        port = self.speaker.port

        if port == str():
            self.get_speaker_data()

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
            data = response.read()

            if str(status) != '200':
                upnp_error = re.search("<errorCode>(.*?)</errorCode>", data, re.MULTILINE)
                if upnp_error is not None:
                    raise BaseException('http_put | Http status {}, upnp error code {} for {}'.format(status,
                                                                                        upnp_error.group(1),
                                                                                        api_action))
                else:
                    raise BaseException("http_put |Http status {} for {}".format(status, api_action))

                data = str()
            else:
                self.log_msg('http_put | Http status {}'.format(status))

        except Exception as e:
            raise BaseException("http_put | Exception: '{}' for {}".format(e, api_action))
            data = str()
        finally:
            if http_client:
                http_client.close()

        return data

    def set_mute(self, do_set_mute):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering set_mute...")
        api_action = '"urn:schemas-upnp-org:service:RenderingControl:1#SetMute"'
        data = get_data_str('<u:SetMute xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">'
                            '<InstanceID>0</InstanceID><Channel>Master</Channel><DesiredMute>{}</DesiredMute>'
                            '</u:SetMute>'.format(int(do_set_mute)))

        return self._http_put("/MediaRenderer/AVTransport/Control", api_action, data) != str()

    def clear_queue(self):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering clear_queue...")
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#RemoveAllTracksFromQueue"'
        data = get_data_str('<u:RemoveAllTracksFromQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID></u:RemoveAllTracksFromQueue>')

        return self._http_put("/MediaRenderer/AVTransport/Control", api_action, data) != str()

    def browse(self, search):
        """
        :return: Server reply. str() in case of error.
        :rtype: str
        """
        print("Entering browse...")
        service_type = "urn:schemas-upnp-org:service:ContentDirectory:1"
        action_name = "Browse"

        api_action = '"{}#{}"'.format(service_type, action_name)
        data = get_data_str('<u:{a} xmlns:u="{b}">'.format(a=action_name, b=service_type) +
                            '<ObjectID>{}</ObjectID>'.format(search) +
                            '<BrowseFlag>BrowseDirectChildren</BrowseFlag>' +
                            '<Filter>*</Filter>' +
                            '<StartingIndex>0</StartingIndex>' +
                            '<RequestedCount>0</RequestedCount>' +
                            '<SortCriteria>+upnp:artist,+dc:title</SortCriteria>' +
                            '</u:{}>'.format(action_name))

        return self._http_put("/MediaServer/ContentDirectory/Control", api_action, data)

    def _unencode(self, text):
        result = text.replace('&lt;', '<')
        result = result.replace('&gt;', '>')
        result = result.replace('&quot;', '"')
        result = result.replace('&apos;', "'")
        result = result.replace('&amp;', '&')
        return result

    def _encode(self, text):
        result = text.replace('&', '&amp;')
        # result = re.sub(r'&(?!amp;)', '&amp;', text)
        result = result.replace('<', '&lt;')
        result = result.replace('>', '&gt;')
        result = result.replace('"', '&quot;')
        result = result.replace("'", '&apos;')
        return result

    def _get_favorites(self, data):
        """
        :return: List of dictionaries of favorites meta data: [{'uri': '', 'title': '', 'meta_data': ''}].
                 Returns [] in case of error
        :rtype: List
        """
        print("Entering _get_favorites...")
        favorites_list = []
        res = re.search("<Result>(.*?)</Result>", data)
        if res == None:
            return favorites_list
        res = res.group(1)
        result = self._unencode(res)

        favorites = re.findall("<item.*?>(.*?)</item>", result)
        for favorite in favorites:
            fav = {}
            title = re.search("<dc:title>(.*?)</dc:title>", favorite, re.MULTILINE)
            if title is not None:
                title = self._unencode(title.group(1))
                fav["title"] = title
            uri = re.search("<res.*?>(.*?)</res>", favorite, re.MULTILINE)
            if uri is not None:
                uri = self._unencode(uri.group(1))
                fav["uri"] = uri
            uri_md = re.search("<r:resMD>(.*?)</r:resMD>", favorite, re.MULTILINE)
            if uri_md is not None:
                fav["meta_data"] = uri_md.group(1)

            favorites_list.append(fav)

        return favorites_list

    def get_fav_data(self, fav_list, fav_name):
        """
        :return: Dictionary of meta data of requested favorite, e.g. {'uri': '', 'title': '', 'meta_data': ''}
        :rtype: Dictionary
        """
        print("Entering get_fav_data...")
        for fav in fav_list:
            if ("title" in fav) and ("uri" in fav) and ("meta_data" in fav):
                if fav_name == fav["title"]:
                    return fav

        return {}

    def select_fst_track(self, ):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering select_fst_track...")
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Seek"'
        data = get_data_str('<u:Seek xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID>'
                            '<Unit>TRACK_NR</Unit>'
                            '<Target>1</Target>'
                            '</u:Seek>')

        return self._http_put("/MediaRenderer/AVTransport/Control", api_action, data) != str()

    def set_playlist_active(self):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering set_playlist_active...")
        if self.speaker.rincon == str():
            self.discovery()

        return self.set_av_transport_uri("x-rincon-queue:{}#0".format(self.speaker.rincon), str()) != str()

    # Playlist Children
    def set_playlist(self, uri, meta_data):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering set_playlist...")
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#AddURIToQueue"'

        data = get_data_str('<u:AddURIToQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID>'
                            '<EnqueuedURI>{}</EnqueuedURI>'
                            '<EnqueuedURIMetaData>{}</EnqueuedURIMetaData>'
                            '<DesiredFirstTrackNumberEnqueued>1</DesiredFirstTrackNumberEnqueued>'
                            '<EnqueueAsNext>1</EnqueueAsNext>'
                            '</u:AddURIToQueue>'.format(uri, meta_data))

        return self._http_put("/MediaRenderer/AVTransport/Control", api_action, data) != str()

    def set_play_mode_shuffle_no_repeat(self):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering set_play_mode_shuffle_no_repeat...")
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#SetPlayMode"'
        data = get_data_str('<u:SetPlayMode xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID>'
                            '<NewPlayMode>SHUFFLE_NOREPEAT</NewPlayMode>'
                            '</u:SetPlayMode>')

        return self._http_put("/MediaRenderer/AVTransport/Control", api_action, data) != str()

    def play(self):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering play...")
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Play"'
        data = get_data_str('<u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID>'
                            '<Speed>1</Speed>'
                            '</u:Play>')

        return self._http_put("/MediaRenderer/AVTransport/Control", api_action, data) != str()

    def play_next(self):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering play_next...")
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Next"'
        data = get_data_str('<u:Next xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID>'
                            '</u:Next>')

        return self._http_put("/MediaRenderer/AVTransport/Control", api_action, data) != str()

    def play_previous(self):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering play_previous...")
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Previous"'
        data = get_data_str('<u:Previous xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID>'
                            '</u:Previous>')

        return self._http_put("/MediaRenderer/AVTransport/Control", api_action, data) != str()

    def pause(self):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering pause...")
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Pause"'
        data = get_data_str('<u:Pause xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID>'
                            '</u:Pause>')

        return self._http_put("/MediaRenderer/AVTransport/Control", api_action, data) != str()

    def set_volume(self, volume):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering set_volume...")
        api_action = '"urn:schemas-upnp-org:service:RenderingControl:1#SetVolume"'
        data = get_data_str('<u:SetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">'
                            '<InstanceID>0</InstanceID>'
                            '<Channel>Master</Channel>'
                            '<DesiredVolume>{}</DesiredVolume>'
                            '</u:SetVolume>'.format(volume))

        return self._http_put("/MediaRenderer/RenderingControl/Control", api_action, data) != str()

    def set_av_transport_uri(self, uri, uri_meta_data):
        """
        :return: Server reply.
        :rtype: str
        """
        print("Entering set_av_transport_uri...")
        encoded_uri = self._encode(self._unencode(uri))
        encoded_uri_meta_data = self._encode(self._unencode(uri_meta_data))
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'
        data = get_data_str('<u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'
                            '<InstanceID>0</InstanceID>'
                            '<CurrentURI>{}</CurrentURI>'
                            '<CurrentURIMetaData>{}</CurrentURIMetaData>'
                            '</u:SetAVTransportURI>'.format(encoded_uri, encoded_uri_meta_data))

        # print("set_av_transport_uri | ...\n- api_action: {}\n- data:       {}".format(api_action, data))

        return self._http_put("/MediaRenderer/AVTransport/Control", api_action, data)

    def play_radio(self, uri, uri_meta_data):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering play_radio...")
        self.set_av_transport_uri(uri, uri_meta_data)
        return self.play()

    def play_playlist(self, uri, meta_data):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering play_playlist...")
        ret = self.clear_queue()
        if not ret:
            raise BaseException("play_playlist | Error clear_queue")

        print("play_playlist | ###\n{}\n{}\n###".format(uri, meta_data))

        ret = self.set_playlist(uri, meta_data)
        if not ret:
            raise BaseException("play_playlist | Error set_playlist")

        ret = self.set_playlist_active()
        if not ret:
            raise BaseException("play_playlist | Error set_playlist_active")

        ret = self.set_play_mode_shuffle_no_repeat()
        if not ret:
            return False

        ret = self.select_fst_track()
        if not ret:
            return False

        return self.play()

    def join_rincon(self, rincon):
        """
        :return: True if server request successfully.
        :rtype: bool
        """
        print("Entering join_rincon...")
        self.set_av_transport_uri("x-rincon:RINCON_{}".format(rincon), str())
        return self.play()

    def get_favorites_data(self, favorite_name):
        ret = self.browse("R:0/2")
        if ret == str():
            raise BaseException("get_favorites_data | Could not retrieve infos regarding favorites.")
        favorites = self._get_favorites(ret)
        if not favorites:
            raise BaseException("get_favorites_data | Could not retrieve favorites meta data.")
            return {}
        fav_data = self.get_fav_data(favorites, favorite_name)
        if ("uri" not in fav_data) or ("meta_data" not in fav_data):
            raise BaseException("get_favorites_data | Favorite '{}' not found".format(favorite_name))

        return fav_data

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        global sonos_system

        if 'sonos_system' not in globals():
            sonos_system = []
            self.discovery()

        self.get_speaker_data()

    def on_input_value(self, index, value):

        try:
            if (index == self.PIN_I_BNEXT) and (bool(value)):
                self.play_next()

            elif index == self.PIN_I_PLAY:
                if value:
                    self.play()
                else:
                    self.pause()

            elif (index == self.PIN_I_BPREVIOUS) and (bool(value)):
                self.play_previous()

            elif index == self.PIN_I_SPLAYLIST:
                if value == str():
                    self.log_msg("on_input_value | Error with radio input. Is empty. Check input value!")
                    return

                fav_data = self.get_favorites_data(value)
                if fav_data == {}:
                    return

                uri = fav_data["uri"]
                meta_data = fav_data["meta_data"]
                self.play_playlist(uri, meta_data)

            elif index == self.PIN_I_SRADIO:
                if value == str():
                    self.log_msg("on_input_value | Error with radio input. Is empty. Check input value!")
                    return

                    fav_data = self.get_favorites_data(value)
                    if fav_data == {}:
                        return

                    uri = fav_data["uri"]
                    meta_data = fav_data["meta_data"]
                    self.play_radio(uri, meta_data)

            elif index == self.PIN_I_NVOLUME:
                if int(value) > 0 or int(value) < 100:
                    self.set_volume(value)
                else:
                    self.log_msg("on_input_value | Error with volume input. Is x < 0 or x > 100. Check input value!")

            elif index == self.PIN_I_SJOINRINCON:
                if value == str():
                    self.log_msg("on_input_value | Error with RINCON input. Is empty. Check input value!")
                    return

                self.join_rincon(self._get_input_value(self.PIN_I_SJOINRINCON))
        except Exception as e:
            self.log_msg(e)

def get_data_str(command):
    data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" ' \
           's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">' \
           '<s:Body>{}</s:Body>' \
           '</s:Envelope>'.format(command)
    return data


global sonos_system


class SonosPlayer:
    def __init__(self):
        self.location = str()
        self.ip = str()
        self.rincon = str()
        self.port = 0
        self.services = {}
        self.name = str()

    def __str__(self):
        return self.name

    def read_device(self, xml_device_root):
        # print("Entering SonosPlayer::read_device...")
        device_dict = {}
        for device in xml_device_root.findall("{urn:schemas-upnp-org:device-1-0}device"):
            udn = device.findtext("{urn:schemas-upnp-org:device-1-0}UDN")
            device_dict[udn] = {}
            device_dict[udn]["friendly_name"] = device.findtext("{urn:schemas-upnp-org:device-1-0}friendlyName")
            device_dict[udn]["roomName"] = device.findtext("{urn:schemas-upnp-org:device-1-0}roomName")
            device_dict[udn]["modelName"] = device.findtext("{urn:schemas-upnp-org:device-1-0}modelName")

            if device_dict[udn]["roomName"] is None:
                # Valid for Media Renderer oder Media Server devices
                continue

            self.name = "{}: {} ({})".format(device_dict[udn]["modelName"], device_dict[udn]["roomName"], self.rincon)
            icon = device.find("{urn:schemas-upnp-org:device-1-0}iconList")
            if icon is not None:
                icon = icon.find("{urn:schemas-upnp-org:device-1-0}icon")
                device_dict[udn]["icon_url"] = icon.findtext("{urn:schemas-upnp-org:device-1-0}url")

            service_list = device.find("{urn:schemas-upnp-org:device-1-0}serviceList")
            if service_list is not None:
                for service in service_list.findall("{urn:schemas-upnp-org:device-1-0}service"):
                    service_id = service.findtext("{urn:schemas-upnp-org:device-1-0}serviceId")
                    device_dict[udn][service_id] = {}
                    device_dict[udn][service_id]["service_url"] = \
                        service.findtext("{urn:schemas-upnp-org:device-1-0}SCPDURL")
                    device_dict[udn][service_id]["control_url"] = \
                        service.findtext("{urn:schemas-upnp-org:device-1-0}controlURL")
                    device_dict[udn][service_id]["service_type"] = \
                        service.findtext("{urn:schemas-upnp-org:device-1-0}serviceType")

            device_list = device.find("{urn:schemas-upnp-org:device-1-0}deviceList")
            if device_list is not None:
                child_device_dict = self.read_device(device_list)
                for child in child_device_dict.keys():
                    device_dict[udn][child] = child_device_dict[child]

        return device_dict

    def get_data(self, path=str()):
        """
        Gets the speakers meta data from the location url

        :param path:
        :return:
        """
        # print("Entering SonosPlayer::get_data...")
        if path is str():
            path = self.location

        try:
            response = urllib2.urlopen(path)
            data = response.read()

            xml_root = ET.fromstring(data)
            self.read_device(xml_root)

        except Exception as e:
            print("get_data | Error: {}".format(e))

    def get_scpd_url(self, service_id):
        print("Entering SonosPlayer::get_scpd_url...")

        try:

            response = urllib2.urlopen(self.get_url())
            data = response.read()

            xml_root = ET.fromstring(data)
            device = xml_root.find("{urn:schemas-upnp-org:device-1-0}device")
            # friendly_name = device.findtext("{urn:schemas-upnp-org:device-1-0}friendlyName")
            # icon = device.find("{urn:schemas-upnp-org:device-1-0}iconList")
            # icon = icon.find("{urn:schemas-upnp-org:device-1-0}icon")
            # icon_url = icon.findtext("{urn:schemas-upnp-org:device-1-0}url")
            # print("get_scpd_url | {}\t{}".format(friendly_name, self.get_url(icon_url)))

        except Exception as e:
            print("get_scpd_url | Error: {}".format(e))

    def get_url(self, path):
        # print("Entering SonosPlayer::get_url...")
        return "http://{}:{}{}".format(self.ip, self.port, path)
