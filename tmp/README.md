# AI Retail Dynamic Allocation Demo

This repo contains the full code for running a demo version of the Dynamic Allocation use case. The demo is intended to run either locally or on the cloud, and is not intended to be used as a full product.

## Getting Started

There are two ways which you can run this demo. Pick the option that works for you below.

### Running without Docker

* Ensure that you have Python 3.8+ and NodeJS 14+ installed.
* Using your terminal on a Mac or Linux based system, use the ```./run.sh``` script.
* For Windows users, use the ```run.bat``` script.
* This script will start both the Python and Node servers.
* Wait some time until you see text saying the app has compiled.
* Access the UI on ```http://localhost:9005```

### Running with Docker

* With Docker installed, run ```docker-compose up --build```
* Access the UI on ```http://localhost:9005```

## How to use

* The app demonstrates a simple example of how dynamic allocation works.
* Upon loading the app, you will see a dropdown with some SKUs. 
* For simplicity reasons, we only demonstrate one SKU at a time, as SKUs are unrelated to each other.
* When a SKU is selected, a list of sources and demands will be presented.
* The sources show how much of that SKU is available at the locations.
* The demand shows how much of that SKU is needed at the locations.
* The user can change which sources are available by ticking or unticking the sources.
* When the user presses optimise, a request is sent to the backend to calculate the most optimal allocation.
* On return, the user is presented with a matrice, showing how to best allocate stock.
* Stock is allocated based on margins. You can press the toggle to see the margin matrice. 
* The user should ideally be able to see roughly how the backend optimiser is working and making decisions.
* The better demonstrate this, use a single source to optimise with, and you can see that the optimiser chooses to allocate based on the highest margin.
* Remember, that margin is based on sale price versus cost price. You can use many metrics to determine allocation. This is just for demo purposes to get the concept across to the user.

## Where to find more information

https://dev.azure.com/aiRetailAnalytics/aiRetailAnalytics/_wiki/wikis/aiRetailAnalytics.wiki/498/Engineering

## Running backend integration tests

1. run command ```pip install pytest``` 
2. cd into ```/server``` directory
3. run command ```pytest``` in terminal


## Running code coverage on backend

1. run command ```pip install coverage```
2. cd into ```/server``` directory
3. run command ```coverage run --source ./app -m pytest```. Note using ```source ./app``` ensures coverage is only 
ran on source code and not on e.g. the ```venv``` or the ```test``` directory for instance. 
4. see results with ```coverage report```
5. alternatively, run command ```coverage html``` to generate html report, and view it by opening the 
```htmlcov/index.html``` in your browser.