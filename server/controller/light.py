# Lighting controller

from ws import BackboneCollection
import gevent
from light_model import *
from lights_dict import *

class LightController(BackboneCollection):
    def __init__(self, lox_ctrl):
        '''initialize the lights as per the list in lights_dict'''
        global light_mapping
        self.generate_lights(light_mapping)

        self.ws = None # make the websocket connection + send auth
        BackboneCollection.__init__(self)

        lox_ctrl.register_listner(self.on_message)
        self.lox_sock = lox_ctrl

    def generate_lights(self, light_mapping):
        '''generate lights list'''
        self.lights = []
        tmp = None
        print light_mapping, "what---------------------------------------------------"
        for each in light_mapping:
            tmp = self.dict_to_light(each)
            tmp.parent = self #set the child to be able to call parent
            print tmp.json()
            self.lights.append(tmp)

    def dict_to_light(self, dic):
        '''converts the dict of light as found in lights_dict and converts it to light object as in light'''
        each = dic
        uuids = each['UUIDs']
        bounds = each['bounds']
        id = each['id']
        typ = each['type']
        zone = each['zone']
        tmp = light(id, typ, zone, uuids['state'], uuids['action_up'], uuids['action_down'])
        tmp.set_val_bounds(bounds['action_low'], bounds['action_high'], bounds['state_low'], bounds['state_high'])
        return tmp

    def ready_to_update(self):
        ''' runs through each lights and makes sure each of them are ready to receive updates'''
        for each in self.lights:
            if each.state_n == -1:
                return False
        return True

    def c2s_update(self, model):
        '''takes the update from the client and relays it to the server'''
        n = model['state_n']
        v = model['value']
        for each in self.lights:
            ret_val = each.get_action_str(n,v)
            if ret_val:
                self.lox_sock.send_message(ret_val)

    def on_message(self, msg):
        ''' parses the incoming message from the main loxone controller'''
        typ = msg['type']
        if typ == "config":
            self.parse_config_msg(msg['msg'])
        elif typ == "state":
            self.parse_state_msg(msg['msg'])

    def parse_config_msg(self, n_uuids):
        ''' parses the uuid to n mapping in msg to set the n values to the lights'''
        for each_light in self.lights:
            for each_n_uuid in n_uuids:
                each_light.set_n(each_n_uuid['n'],each_n_uuid['UUID'])

    def parse_state_msg(self, states):
        '''parses the state message and updates appropriate light'''
        print states, '--trying to parse'
        for each in states:
            n = each['n']
            v = each['v']
            for each_light in self.lights:
                ret_val =  each_light.try_update(n,v)
                if ret_val:
                    self.update(each_light.json())
                    print each_light.id, "|n:" ,n, "|v:",v, "|val:", ret_val

    def do_save(self, data):
        '''relay it to client to server update function'''
        print data, 'received---------------------'
        self.c2s_update(data)
