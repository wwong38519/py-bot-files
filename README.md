### py-bot-files

#### Description
* A simple Telegram bot to save received files and to list files for download

#### How to run
* Replace 'token' with Your Bot Token in [config.py](config.py)
```python
token = 'token'
```
* Build Docker Image
```shell
docker build -t pybotfiles .
```
* Run
  * `~/Downloads/files` is an example path on the host
  * On Windows host, the path could be `//c/Users/wwong38519/Downloads/files`
  * `/usr/src/files` is the path in the container as setup in [config.py](config.py)
```shell
docker run -it --rm -v ~/Downloads/files:/usr/src/files --name run-pybotfiles pybotfiles
```
* Run in detached mode
```shell
docker run -d -v ~/Downloads/files:/usr/src/files --name run-pybotfiles pybotfiles
```
* Stop and remove container
```shell
ID=$(docker stop run-pybotfiles)
docker rm $ID
```
