docker build --platform linux/amd64 -t wics-term-project .
docker tag wics-term-project hravishankar/wics-term-project
docker push hravishankar/wics-term-project