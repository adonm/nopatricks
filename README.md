# nopatricks

Requires [Python 3](https://www.python.org), and ideally a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/). 

Usage:
```
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
./launcher.py --source SOURCE.mdl --target TARGET.mdl OUTPUT.mdt
```
