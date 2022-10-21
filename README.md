# A zero configuration HTTP caching proxy

- no installation required
- just run it in this directory: `python3 httpcache.py`
- useful for development of Alpine containers
- [original](https://gist.githubusercontent.com/Jegeva/dafe74058ea30495c84c536a142a1144/raw/c559f29d7aa8ff28ef29d403fd54d2749e2ab19c/httpcache.py)


## Rootless Podman

Start the caching proxy

```
python httpcache.py
```

Podman uses your network

```
CONTAINER=$(buildah from scratch)
export http_proxy=http://localhost:8000
~/alpine-make-rootfs/alpine-make-rootfs ... rootfs.tar
buildah add $CONTAINER rootfs.tar /
```

## Docker

Docker runs on its own network, so you have to bind to its interface

```
python httpcache.py -b 172.17.0.1
```

```
docker build --build-arg http_proxy=http://172.17.0.1:8000 -t container .
```

Docker compose [has to be handled differently](https://stackoverflow.com/questions/54218632)

```
mkdir /etc/systemd/system/docker.service.d
cat>/etc/systemd/system/docker.service.d/http-proxy.conf<<EOF
[Service]
Environment="HTTP_PROXY=http://172.17.0.1:8000" "http_proxy=http://172.17.0.1:8000"
EOF
systemctl daemon-reload
systemctl show docker --property Environment
systemctl restart docker
```
