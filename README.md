# __Keyboard Chattering Fix for Linux__

[![GitHub](https://img.shields.io/github/license/w2sv/KeyboardChatteringFix-Linux?)](LICENSE)

__A tool for filtering mechanical keyboard chattering on Linux__

## The problem

Switches on mechanical keyboards occasionally start to "chatter",
meaning when you press a key with a faulty switch it erroneously detects
two or even more key presses.

## The existing solutions

Apart from buying a new keyboard, there have been ways to deal
with this problem using software methods. The idea is to filter key presses
that occur faster than a certain threshold. "Keyboard Chattering Fix v 0.0.1"
is a tool I had been using on Windows for a long time, and these days you also have
[Keyboard Chatter Blocker](https://github.com/mcmonkeyprojects/KeyboardChatterBlocker),
which is a nice open source tool with some additional functionality. It's actually what
I use myself when I use Windows.

Unfortunately, all existing tools only work on Windows.
On Linux, the answer everyone seems to give is to use the Bounce Keys feature of X,
but it's not really useful in this way. For one, it resets the delay even on filtered
key presses, meaning that if you press the key fast enough,
*none* of the presses with pass through, ever. And if the key chatters,
this is bound to happen eventually and interfere with fast repeated key presses.

## This project's solution

This tool attempts to solve any such problems that may arise by having full low-level access
and control over all keyboard events.
Using `libevdev`'s Python bindings, it grabs your keyboard's event device and processes its events,
then outputs the result back to the system using `/dev/uinput`, effectively emulating a keyboard -
one that doesn't chatter, unlike your real one!

This also means it works across the system, without depending on X.

As for the filtering rule, what seems to work well is the time between the last key up event
and the current key down event. When the key chatters, that time seems to be very low - around 10 ms.
By filtering such anomalies, we can hopefully remove chatter without impeding actual fast key presses.

## Installation

Download the repository as a zip and extract the file. The dependencies are listed in the requirements.txt. And you can install it with the command below. 

```shell
sudo pip3 install -r requirements.txt
```

## Usage

`cd` inside the location of the KeyboardChatteringFix-Linux-master extracted folder and enter the command below to run.

```shell
sudo python3 -m src
```

### Customization Options

- -k KEYBOARD, --keyboard KEYBOARD
  - Name of your chattering keyboard device as listed in /dev/input/by-id. If left unset, will be attempted to be retrieved
  automatically. The device is captured `by-id`, and therefore in a persistent way.

- -t THRESHOLD, --threshold THRESHOLD
  - Filter time threshold in milliseconds. Default=30ms. Note: This does not denote the time between key presses, but
    between a key being
    released and pressed again, so the number should probably be lower than you might think. For reference, if you
    press the key really fast this delay is around 50 ms.

- -v {0,1,2}, --verbosity {0,1,2}

## Automation

Starting the script manually every time doesn't sound like the greatest idea, so
you should probably consider something that does it for you. Modify the `chattering_fix.sh` to `cd` into the absolute path of the downloaded folder and input the keyboard id and the desired threshold. For example:
```shell
cd /home/foouser/Downloads/KeyboardChatteringFix-Linux-master/ && sudo python3 -m src -k usb-SINO_WEALTH_USB_KEYBOARD-event-kbd -t 50
```
Also, make sure to change the file permission of `chattering_fix.sh` so that it is executable.
```shell
chmod +x chattering_fix.sh
```
The `chattering_fix.service` file should also be edited. The `ExecStart` should be the absolute path of the `chattering_fix.sh`. For example:
```shell
ExecStart=/home/foouser/Downloads/KeyboardChatteringFix-Linux-master/chattering_fix.sh
```
Then, copy the `chattering_fix.service` to `/etc/systemd/system/` and enable it with the command below.
```shell
systemctl enable --now chattering_fix
```
You can check if the systemd unit file is properly working using 
```shell
systemctl status chattering_fix.service
```
You can also use 
```shell
journalctl -xeu chattering_fix.service
```
just to make sure that there are no errors.