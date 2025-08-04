
class Extension:

    def __init__(self, *args, **kwargs):
        self.data = {
                'extension': '?',
                'callsign': '',
                'displayname': '',
                'devicetype': 'unknown',
                'state': 'UNKNOWN',
                'exchange': '',
        }
        self.update(**kwargs)

    def update_state(self, state, devicetype):
        changed = False
        if self.data.get('state') != state:
            self.data['state'] = state
            changed = True
        if self.data.get('state') != devicetype:
            self.data['devicetype'] = devicetype
            changed = True
        return changed

    def update(self, *args, **kwargs):

        changed = False
        ext = self.data.get('extension')


        for k,v in kwargs.items():
            if self.data.get(k) != v:
                self.data[k] = v
                changed = True
                print(f'{ext}/{k}={v}')
        return changed

    def get(self):
        return self.data



class DataStore:

    def __init__(self):
        self.phonebook = {}
        self.items = len(self.phonebook.keys())

    def update(self, data, config):
        datatype = data.pop('_data')

        if datatype == 'phonebook':
            return self.phonebook_update(data, config)

        if datatype == 'state':
            return self.state_update(data, config)

        print(f'Unknown datatype {datatype}')


    def phonebook_update(self, data, config):
        service = str(data.get('extension'))

        if service is not None:
            tm = config.get('TrunkMap', {})
            if service in tm:
                for k, v in tm.get(service).items():
                    data[k] = v

            xchg = str(data.get('exchange'))
            key = f'{xchg}:{service}'
            print(f'updating phonebook for {key}')

            if key not in self.phonebook:
                print(f'Service did not exist, creating with {data}')
                self.phonebook[key] = Extension(**data)

            elif self.phonebook[key].update(data) is not None:
                print(f'Service did exist, updated with {data}.')

        return None


    def state_update(self, data, config):

        data['extension'] = data.get('Service')
        state = data.get('State')
        service = str(data.get('extension'))

        if service is not None:
            xchg = str(data.get('exchange'))
            key = f'{xchg}:{service}'
            print(f'updating state for {key}')
            if key not in self.phonebook:
                self.phonebook[key] = Extension(extension=service, devicetype=data.get('DeviceType'), exchange=xchg, state=state)

            if self.phonebook[key].update_state(state, data.get('DeviceType')):
                return { 'extension': service, 'state': state, 'exchange': xchg }


    def get_phonebook(self):
        return  [ y.get() for x,y in self.phonebook.items() ]

    def get_extension(self, ext):
        ext = str(ext)
        pb = self.phonebook.get(ext)
        if pb is None:
            print(f'Cannot read extension {ext}')
        return pb


datastore = DataStore()

