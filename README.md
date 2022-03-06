## Setup

1. Install pip
2. Install virtualenv `pip install virtualenv`
3. Create virtual env `virtualenv venv`
4. Install dependencies `pip install -r requirements.txt`
5. Establish your local.env file as stated below

## Necessary Env Vars to go into local.env

- AWS_ACCESS_KEY_ID=duh
- AWS_SECRET_ACCESS_KEY=duh
- BUCKET_ID=s3 bucket id
- CONFIG_PATH=path in s3 bucket containing additional config data

## How to use

First set your venv

`source venv/bin/activate`

then download the data

`src/run download`

then run the application

`src/run analyze`

## How to update the classification rules

Classification rules is composed of a list of objects under the property `rules`
Each object can be a rule or a rule group

A rule is composed of a name and statements
If there is more than one statement, all statements must pass in order for the rule to apply

```yaml
rules:
  - name: Rent
    statements:
      - type: substring
        params:
          string: RENTAL PAYMENT
      - type: abs-amt
        params:
          amt: 350
```

A rule group is composed of a description and a list of rules. Used marking rules as related to each other and doesn't affect classification, these groups are flattened during analysis.

```yaml
rules:
  - description: Group of rules for my overseas trips
    rules:
      - name: Candy
        statements:
          - type: substring
            params:
              string: Cadbury
      - name: Hostels
        statements:
          - type: substring
            params:
              string: HOSTEL CHECKOUT
```

### List of possible statement types

- substring: will match true if the given string matches any substring of the transaction description
- abs-amt: will match true if the given amt parameter matches the absolute value of the transaction amount

```yaml
rules:
  - name: Yugioh Cards
    statements:
      - type: abs-amt
        params:
          amt: 9.99
```

- date: will match true if the given iso parameter matches the date of the transaction

```yaml
rules:
  - name: Splurge day
    statements:
      - type: date
        params:
          iso: 2021-11-23
```

## How to mark transactions as ignored?

Specially handled classifications are listed in [this file](src/compile.py)
