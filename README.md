# SpaceAPI Directory Mirror

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
