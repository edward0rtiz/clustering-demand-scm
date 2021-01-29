# Kiwibot Analytic Dashboard (KAD) :robot:


> KAD is an KAD is a tool to get comprehensive analytics about kiwibot business and create strategies for supply the demand of kiwibots in key areas based in a cluster prediction of hot spot zones. To use this tool select in the navigation bar the insights you want to explore and get the information updated in real-time.

# Landing Page

click [here](http://34.123.103.23:8050/) to see KAD tool in action


# Quick Start


KAD is very easy to install and deploy in a Docker container. By default, the Docker image need to be will exposed on port 8050, so change this within the Dockerfile if necessary when pulling the files or . When ready, simply use the Dockerfile to build the image.

### Install on terminal using github

> Download the repository in your terminal
```
git clone https://github.com/edward0rtiz/clustering-demand-scm.git
```
> Create the image based in the docker-compose.yml from the repo
```
docker-compose build
```
> Once the image is downloaded, create the container running as background process
```
docker-compose up -d
```
> open the tool in your localhost

### Install on terminal using Docker
> In your terminal pull the image from docker hub
```
docker pull edward0rtiz/kiwibot-kda:v1.0
```
> Once the image is created run the image to create a container exectuded in background
```
docker run -d -p 8050:8050 <CONTAINER NAME>:<TAG>
```
> If you want to stop the tool
```
docker stop <CONTAINER ID>
```
> If you want to restart the tool

```
dokcer start -ai <CONTAINER ID>
```
> open the tool in your localhost:8050

# Credentials
Before deploying the applicaton credentials with AWS must be configured. Once the repo ins downloaded create a .env fileto put the AW credentials

```
$ mkdir /.env
$ cat >> ~/.env/
[default]
aws_access_key_id=YOUR_ACCESS_KEY_HERE
aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
```

# Stack

KAD uses a number of tools, frameworks and libraries to work properly

**Front-End**:

| Tool/Library                            | Version |
| --------------------------------------- | ------- |
| [DASH-Plotly](https://dash.plotly.com/) | ^1.19   |

**Back-End**:

| Tool/Library                                               | Version |
| ---------------------------------------------------------- | ------- |
| [Python](https://www.python.org/)                          | ^3.8    |
| [Flask](https://flask.palletsprojects.com/en/1.1.x/)       | ^1.1.2  |
| [Pandas](https://www.django-rest-framework.org/)           | ^1.2.1  |
| [Numpy](https://www.postgresql.org/)                       | ^1.19.5 |
| [Geocoder](https://geocoder.readthedocs.io/)               | ^1.38.1 |
| [Selenium](https://selenium-python.readthedocs.io/)        | ^3.14   |
| [Scikit-learn](https://scikit-learn.org/stable/index.html) | ^0.24   |

View the complete list of back-end dependencies in the corresponding [requirements.txt](https://github.com/edward0rtiz/commodoro/blob/master/requirements.txt).

**Packaging/Deployment**:

| Tool/Library                                | Version  |
| ------------------------------------------- | -------- |
| [GCP VM](https://cloud.google.com/compute/) | ^10.16.0 |
| [S3](https://aws.amazon.com)                | ^1.17.3  |
| [Docker](https://docs.docker.com/)          | ^19.01.6 |

# Team

 - Edward Ortiz - [linkedin](https://www.linkedin.com/in/ortizedward/) & [Github](https://github.com/edward0rtiz)
 - Carlos Molano - [linkedin](https://www.linkedin.com/in/carlos-molano-salazar/) & [Github](https://github.com/cmmolanos1)

License
----

MIT License
