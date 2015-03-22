# Neurio → Wink Nimbus Integration Service
Display the current power consumption from a Neur.io sensor on a Wink Nimbus clock dial.

## Setup

### 1. Pull git submodules

```
$ git submodule init
$ git submodule update
```

### 2. Install additional Python modules

See ``requirements.txt``.

You can install them using pip:

 ```
 $ pip install -r requirements.txt
 ```

### 3. Request Neurio and Wink API keys

You'll need to request these keys from Neurio and Wink. See:

  * http://branch.com/b/wink-api
  * http://community.neur.io/

### 4. Edit configuration Files

Open the files in ```./cfg``` and edit them to set your API
keys and application preferences:

  * ```app.cfg``` – global application preferences
  * ```neurio.cfg``` – Neurio API key settings
  * ```wink.cfg``` – Wink API key settings

### 5. Run application

```
$ python neurio-nimbus.py
```

## Docker

If you'd like, you can run this application in a
[Docker](https://www.docker.com/) image. A Dockerfile
has been included with the project.
