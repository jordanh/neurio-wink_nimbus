#!/usr/bin/env python

import sys
sys.path.append("./py-wink")
sys.path.append("./python-neurio")

import wink
import neurio

import ConfigParser
import time
import datetime


class Nimbus(object):
    def __init__(self, secret_file_name):
        w = wink.init(secret_file_name)

        if "cloud_clock" not in w.device_types():
            raise RuntimeError(
                "you do not have a cloud_clock associated with your account!"
            )

        # Wrap cloud_clock with Nimbus object
        c = w.cloud_clock()
        self.__class__ = type(c.__class__.__name__,
                              (self.__class__, c.__class__),
                              {})
        self.__dict__ = c.__dict__

    def set_dial_percent(self, dial_num, percent, label):
            dial = self.dials()[dial_num]
            original = dial.get_config()
            min_value = original["dial_configuration"]["min_value"]
            max_value = original["dial_configuration"]["max_value"]
            value = str(int(percent * 100 / max_value))

            # assert manual control with new value and label:
            dial.update(dict(
                channel_configuration=dict(channel_id="10"),
                dial_configuration=original["dial_configuration"],
                label=label,
                value=percent,
            ))


class Neurio(object):
    def __init__(self, secret_file_name, sensor_id):

        config = ConfigParser.RawConfigParser()
        config.read(secret_file_name)

        tp = neurio.TokenProvider(key=config.get('auth','key'),
                                  secret=config.get('auth','secret'))
        nc = neurio.Client(token_provider=tp)

        # Wrap Neurio client with our Neurio class:
        self.__class__ = type(nc.__class__.__name__,
                              (self.__class__, nc.__class__),
                              {})
        self.__dict__ = nc.__dict__
        self.sensor_id = sensor_id


    def getSample(self):
        sample = self.getLastLiveSamples(sensor_id=self.sensor_id)

        return sample['consumptionPower']


def scale_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def main():
    my_nimbus = Nimbus("./wink-secret.cfg")
    my_neurio = Neurio("./neurio-secret.cfg", "0x0013A20040B65FAD")

    while 1:
        sample = my_neurio.getSample()
        percent = scale_value(sample, 0, 2500, 0, 100)
        current_time = datetime.datetime.now().time()
        print "%s value = %sW, %s%%" % (current_time.isoformat(), sample, percent)
        my_nimbus.set_dial_percent(3, percent, "%sW" % sample)
        time.sleep(60)

    print my_neurio.getSample()

    return 0


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
