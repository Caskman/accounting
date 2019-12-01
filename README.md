
## Necessary Env Vars to go into local.env

AWS_ACCESS_KEY_ID=duh
AWS_SECRET_ACCESS_KEY=duh
BUCKET_ID=data source
CONFIG_PATH=path in s3 bucket containing additional config data
DOCKERENV=1

The presence of DOCKERENV tells the container not to load dev env file, but when not running in docker the app can't see it as it explicitly loads it from the local.env file

