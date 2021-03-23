# SpaceAPI Directory Mirror

This is server mirror the SpaceAPI Directory. It also provides a Web-GUI for the SpaceAPI. Find a demopage [here](directorymirrorserver.noppelmax.online). Unfortunately statistics are currently not running right now.

## Install
Install anaconda.

```
conda create --name directorymirrorserver python=3.5
conda activate directorymirrorserver
pip install flask requests
```

## Run
```
conda activate directorymirrorserver
bash run.sh
```

### Apache2
Setze `AllowEncodedSlashes On` in der Route.

## Licence
Siehe [LICENCE](LICENCE.md)
