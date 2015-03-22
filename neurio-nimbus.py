#!/usr/bin/env python

import sys, traceback
sys.path.append("./py-wink")
sys.path.append("./python-neurio")

import wink
import neurio

import ConfigParser
import time
import datetime


def scale_value(x, in_min, in_max, out_min, out_max):
    try:
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
    except ZeroDivisionError:
        return 0


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

        # keep locally seen ranges for scaling purposes:
        self.min_value = sys.maxint
        self.max_value = 0

    def set_dial_value(self, dial_num, value, label):
            if value < self.min_value:
                self.min_value = value
            if value > self.max_value:
                self.max_value = value

            dial = self.dials()[dial_num]
            # the dial servo will always display a percentage [0..100],
            # we'll set up the dial minimum and maximum to reflect that:
            dial_config = {
                "scale_type": "linear",
                "rotation": "cw",
                "min_value": 0,
                "max_value": 100,
                "min_position": 0,
                "max_position": 360,
                "num_ticks": 12
            }

            # calculate percentage:
            percent = scale_value(value, self.min_value, self.max_value, 0, 100)

            # log statement:
            current_time = datetime.datetime.now().time()
            print "%s percent = %d%%, label = %s, actual = %d [%d, %d]" % (
                current_time.isoformat(), percent, label,
                value, self.min_value, self.max_value)

            # assert manual control (chan. 10) with new config, value, & label:
            dial.update(dict(
                channel_configuration=dict(channel_id="10"),
                dial_configuration=dial_config,
                label=label,
                value=percent,
            ))


class Neurio(object):
    def __init__(self, secret_file_name):
        config = ConfigParser.RawConfigParser()
        config.read(secret_file_name)

        tp = neurio.TokenProvider(key=config.get('auth','key'),
                                  secret=config.get('auth','secret'))
        sensor_id = config.get('device', 'id')
        nc = neurio.Client(token_provider=tp)

        # Wrap Neurio client with our Neurio class:
        self.__class__ = type(nc.__class__.__name__,
                              (self.__class__, nc.__class__),
                              {})
        self.__dict__ = nc.__dict__
        self.sensor_id = sensor_id


    def getSample(self):
        sample = self.get_samples_live_last(sensor_id=self.sensor_id)

        return int(sample['consumptionPower'])


def main():
    app_cfg = ConfigParser.RawConfigParser()
    app_cfg.read("./cfg/app.cfg")

    my_nimbus = Nimbus("./cfg/wink.cfg")
    my_neurio = Neurio("./cfg/neurio.cfg")

    update_period_sec = int(app_cfg.get('global', 'update_period_sec'))

    while 1:
        wattage = my_neurio.getSample()
        my_nimbus.set_dial_value(3, wattage, "%dW" % wattage)
        time.sleep(update_period_sec)

    # normally, we should never return...
    return -1


if __name__ == "__main__":
    # do forever, unless we receive SIGINT:
    while 1:
        try:
            ret = main()
        except KeyboardInterrupt:
            ret = 0
            break
        except:
            print "Exception:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            continue

    sys.exit(ret)
