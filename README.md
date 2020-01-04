## Setup

1. Install pip
2. Install virtualenv `pip install virtualenv`
3. Create virtual env `virtualenv venv`
4. Install dependencies `pip install -r requirements.txt`
5. Establish your local.env file as stated below

## Deploy

Run the `deploy` script

## Update dependencies

After setup, run `pip-compile --upgrade`

## Necessary Env Vars to go into local.env

- AWS_ACCESS_KEY_ID=duh
- AWS_SECRET_ACCESS_KEY=duh
- BUCKET_ID=data source
- CONFIG_PATH=path in s3 bucket containing additional config data
