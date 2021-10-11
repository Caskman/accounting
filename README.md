## Setup

1. Install pip
2. Install virtualenv `pip install virtualenv`
3. Create virtual env `virtualenv venv`
4. Install dependencies `pip install -r requirements.txt`
5. Establish your local.env file as stated below

## Necessary Env Vars to go into local.env

- AWS_ACCESS_KEY_ID=duh
- AWS_SECRET_ACCESS_KEY=duh
- BUCKET_ID=data source
- CONFIG_PATH=path in s3 bucket containing additional config data

## Download Data

First set your venv

`source venv/bin/activate`

then download the data

`python src/download_data.py`

then you'll want to validate the data

`python src/validate_local_data.py`

## Run the application

While in the venv run the following

`src/run analyze`
