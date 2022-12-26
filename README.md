# mihelectrobot
Telegram bot that automatically sends notifications when electricity supply changes.
It requires GPIO pin connected to a signal that represents electricity state.

## Requirements

 * Orange Pi zero
 * `pip install OPi.GPIO`
 * `pip install python-telegram-bot`

## Installation

Copy mihelectrobot directory to /opt
```
cd /opt
git clone git@github.com:tearandfix/mihelectrobot.git
```

Install systemd service
```
cp /opt/mihelectrobot/mihelectrobot.service /lib/systemd/system/
systemctl enable mihelectro.service
systemctl start mihelectro.service
```

## Checking the logs
```
journalctl -f -u mihelectrobot
```

## Run unit tests
```
python3 -m unittest
```
