class light(object):
    def __init__(self, id, typ, zone, state_uuid, up_uuid, down_uuid=""):
        '''init'''
        self.up_uuid = up_uuid
        self.down_uuid = down_uuid
        self.state_uuid = state_uuid
        self.id = id
        self.typ = typ 
        self.zone = zone
        if typ not in ['digital','analog','rgb']:
            raise Exception('Invalid light type'+typ)
            return False
        self.init_values()

    def init_values(self):
        '''initializes values to their defaults'''
        self.state_n = self.action_high = self.action_low = self.state_high = self.state_low = -1
        self.value = str()

    def set_n(self, n,uuid):
        '''compared the uuid to internal uuids and sets the n appropriately if n found'''
        if uuid == self.state_uuid:
            self.state_n = int(n)
            print "uuid hit", self.id
            return True
        else:
            return False

    def set_val_bounds(self, action_low,action_high, state_low,state_high):
        ''' give the bounds of the values of action and state expected'''
        if action_low > action_high or state_low > state_high:
            raise Exception('Invalid bounds set for'+self.id)
            return False
        self.action_high = float(action_high)
        self.action_low = float(action_low)
        self.state_low = float(state_low)
        self.state_high = float(state_high)

    def scale_me(self, v, a, b, x, y):
        '''scales v from [a,b] to [x,y] range'''
        v = float(v)
        a = float(a)
        b = float(b)
        x = float(x)
        y = float(y)
        if b < a or y < x or v < a or v > b:
            raise Exception("Value out of bounds")
            return False
        percent = (v-a) / (b-a)
        final = x + (percent*(y-x))
        return final

    def try_update(self, n, value):
        ''' parse the state update values'''
        # if type(value) != str or type(n) != str:
        #     raise Exception("Type mismatch")
        n = int(n)
        if self.state_n != n:
            return False
        if self.typ == "rgb":
            return self.update_rgb(value)
        else:
            return self.update_analog(value)

    def update_rgb(self, value):
        ''' assuming hex FFFFFF input which is converted to suit local value'''
        value = str(int(float(value)))
        if int(value) > self.state_high or int(value) < self.state_low:
            raise Exception("RGB state value received out of bounds")
            return False
        self.value = self.int_to_hex(value.zfill(9))
        return self.value

    def int_to_hex(self, int_val):
        ''' assumes input values are in format 'rrrgggbbb'  and outputs hex value "AABBCC"'''
        int_val = int_val.zfill(9)
        i = 0
        #split the input into three separate values
        blue_int = int(int_val[i+0:i+3])
        green_int = int(int_val[i+3:i+6])
        red_int = int(int_val[i+6:i+9])

        red_hex = hex(int(self.scale_me(red_int,0,100,0,255)))[2:]
        green_hex = hex(int(self.scale_me(green_int,0,100,0,255)))[2:]
        blue_hex = hex(int(self.scale_me(blue_int,0,100,0,255)))[2:]

        final_val = red_hex.zfill(2) + green_hex.zfill(2) + blue_hex.zfill(2)
        return final_val

    def hex_to_int(self, hex_val):
        ''' "AABBCC" -> "rrrgggbbb" '''
        hex_val = hex_val.zfill(6)
        i = 0 #starting index of the main 6 chars in the string

        red = int(hex_val[i:i+2],16)
        green = int(hex_val[i+2:i+4],16)
        blue = int(hex_val[i+4:i+6],16)

        red_scaled = str(int(self.scale_me(red, 0,255,0,100)))
        green_scaled = str(int(self.scale_me(green, 0,255,0,100)))
        blue_scaled = str(int(self.scale_me(blue, 0,255,0,100)))

        final_val = blue_scaled.zfill(3)+green_scaled.zfill(3)+red_scaled.zfill(3)
        return final_val

    def update_analog(self,value):
        '''update function for updating state of a digital/analog devices'''
        value = float(value)
        scaled_val = self.scale_me(value,self.state_low, self.state_high, 0, 100)
        self.value = str(scaled_val)
        return self.value

    def json(self):
        '''implement based on what the front-end needs'''
        return{
            'up_uuid': str(self.up_uuid),
            'down_uuid':str(self.down_uuid),
            'state_uuid':str(self.state_uuid),
            'id':str(self.id),
            'zone':str(self.zone),
            'type':str(self.typ),
            'value':str(self.value),
            'action_high':str(self.action_high),
            'action_low':str(self.action_low),
            'state_low':str(self.state_low),
            'state_high':str(self.state_high),
            'state_n':str(self.state_n),
            'id':str(self.id)
        }

    def get_action_str(self, n, value):
        '''returns action string to be sent to the socket scaled as per action range'''
        print "HOLA", self.id, n, value
        if self.state_n != int(n):
            return False
        if self.typ == "rgb":
            return self.rgb_action_str(value)
        else:
            return self.analog_action_str(value)

    def rgb_action_str(self,value):
        '''converts to appropriate value readable by the server'''
        int_val = self.hex_to_int(value)
        return "jdev/sps/io/"+self.up_uuid+"/AI/"+str(int_val)

    def analog_action_str(self,value):
        value = float(value)
        uuid = self.down_uuid
        if value > self.value:
            uuid = self.up_uuid
        final_val = self.scale_me(value, 0, 100, self.action_low, self.action_high)
        return "jdev/sps/io/"+uuid+"/"+str(final_val)

def test():
    test_light = light('id', 'rgb', 'zone', 'state_uuid', 'up_uuid')
    test_light.set_val_bounds(0,100100100,0,100100100)
    test_light.set_n('stateUUID',5)
    return test_light
