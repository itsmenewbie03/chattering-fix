import logging
from collections import defaultdict
from typing import DefaultDict, Dict, NoReturn

import libevdev

# HACK: only my M key is chattering so we will only filter that

blocklist = [libevdev.EV_KEY.KEY_M]


def filter_chattering(evdev: libevdev.Device, threshold: int) -> NoReturn:
    # grab the device - now only we see the events it emits
    evdev.grab()
    # create a copy of the device that we can write to - this will emit the filtered events to anyone who listens
    ui_dev = evdev.create_uinput_device()

    logging.info("Listening to input events my dick...")

    while True:
        # since the descriptor is blocking, this blocks until there are events available
        for e in evdev.events():
            if _from_keystroke(e, threshold):
                ui_dev.send_events(
                    [e, libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                )


def _from_keystroke(event: libevdev.InputEvent, threshold: int) -> bool:
    # no need to relay those - we are going to emit our own
    if event.matches(libevdev.EV_SYN) or event.matches(libevdev.EV_MSC):
        return False

    # some events we don't want to filter, like EV_LED for toggling NumLock and the like, and also key hold events
    if not event.matches(libevdev.EV_KEY) or event.value > 1:
        logging.debug(f"FORWARDING {event.code}")
        return True

    if not event.code in blocklist:
        logging.info(f"FORWARDING |{event.code}| as it's not in the blocklist")
        return True

    # the values are 0 for up, 1 for down and 2 for hold
    if event.value == 0:
        if _key_pressed[event.code]:
            logging.debug(f"FORWARDING {event.code} up")
            _last_key_up[event.code] = event.sec * 1e6 + event.usec
            _key_pressed[event.code] = False
            return True
        else:
            logging.info(f"FILTERING {event.code} up: key not pressed beforehand")
            return False

    prev = _last_key_up.get(event.code)
    now = event.sec * 1e6 + event.usec

    if prev is None or now - prev > threshold * 1e3:
        logging.debug(f"FORWARDING {event.code} down")
        _key_pressed[event.code] = True
        return True

    logging.info(
        f"FILTERED {event.code} down: last key up event happened {(now - prev) / 1E3} ms ago"
    )
    return False


_last_key_up: Dict[libevdev.EventCode, int] = {}
_key_pressed: DefaultDict[libevdev.EventCode, bool] = defaultdict(bool)
