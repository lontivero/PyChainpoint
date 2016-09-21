# pychainpoint



A Python module for validating Chainpoint blockchain receipts

### Installation

```
$ pip install proof-of-existence-chainpoint-py
```

### Usage

Use the is_valid_receipt function to validate your Chainpoint receipt.
```python
chainpoint_validate.is_valid_receipt(receipt)

#  receipt - the receipt to be validated, as a string
```

#### Example

```python
from proof_of_existence import Chainpoint

receipt = '''{
    "header": {
        "chainpoint_version": "1.1",
        "hash_type": "SHA-256",
        "merkle_root": "5faa75ca2c838ceac7fb1b62127cfba51f011813c6c491335c2b69d54dd7d79c",
        "tx_id": "b84a92f28cc9dbdc4cd51834f6595cf97f018b925167c299097754780d7dea09",
        "timestamp": 1445033433
    },
    "target": {
        "target_hash": "cbda53ca51a184b366cbde3cb026987c53021de26fa5aabf814917c894769b65",
        "target_proof": [{
            "parent": "4f0398f4707c7ddb8d5a85508bdaa9e22fb541fa0182ae54f25513b6bd3f8cb9",
            "left": "cbda53ca51a184b366cbde3cb026987c53021de26fa5aabf814917c894769b65",
            "right": "a52d9c0a0b077237f58c7e5b8b38d2dd7756176ca379947a093105574a465685"
        }, {
            "parent": "5faa75ca2c838ceac7fb1b62127cfba51f011813c6c491335c2b69d54dd7d79c",
            "left": "4f0398f4707c7ddb8d5a85508bdaa9e22fb541fa0182ae54f25513b6bd3f8cb9",
            "right": "3bd99c8660a226a62a7df1efc2a296a398ad91e2aa56d68fefd08571a853096e"
        }]
    }
}'''
validator = Chainpoint()
result = validator.is_valid_receipt(receipt)
```

##### Sample Valid Result
```python
dict(
  is_valid=True,
  type: 'BTCOpReturn',
  source_id: 'f3be82fe1b5d8f18e009cb9a491781289d2e01678311fe2b2e4e84381aafadee',
  exists: true
)
```


##### Sample Invalid Result
```python
dict(
  is_valid=False,
  error='Cannot parse receipt JSON'
)
```
