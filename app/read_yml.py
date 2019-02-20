
import yaml


class ReadYml:
    config_yml = None

    def __init__(self):
        with open('app/config.yml', 'r') as f:
            self.config_yml = yaml.load(f)

    def get_location(self):
        locations = []
        for i in self.config_yml:
            if 'global_parametrs' in i.lower():
                continue
            locations.append(i)
        return locations

    def get_rack(self, locations):
        racks = []
        for i in self.config_yml[locations]:
            racks.append(i)
        return racks

    def get_all(self):
        d = {}
        for dc in self.config_yml:
            if 'global_parametrs' in dc.lower():
                continue
            d[dc] = []
            for rack in self.config_yml[dc]:
                d[dc].append(rack)
        return d

if __name__ == '__main__':

    y = ReadYml()
    y.get_all()
    print(y.get_location())
