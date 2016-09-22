import re
import json
import hashlib
from merkletools import MerkleTools


class Chainpoint(object):
    CHAINPOINT_VALID_VERSIONS = ['1.0', '1.1', '2']
    CHAINPOINTv1_VALID_HASHTYPES = ['SHA-256']
    CHAINPOINTv2_VALID_HASHTYPES = ['SHA224', 'SHA256', 'SHA384', 'SHA512', 'SHA3-224', 'SHA3-256', 'SHA3-384',
                                    'SHA3-512']
    CHAINPOINTv2_VALID_ANCHORTYPES = ['BTCOpReturn']

    def as_complex(dct):
        if 'target_hash' in dct:
            return complex(dct['real'], dct['imag'])
        return dct

    def isValidReceipt(self, receipt_json):
        receipt = json.loads(receipt_json)
        receipt_version = None
        if 'header' in receipt:
            # header section was found, so this could be a pre-v2 receipt
            receipt_version = receipt[u'header']['chainpoint_version']
        else:
            # no header was found, so it is not a v1.x receipt, check for v2
            if 'type' in receipt:
                type = receipt['type']
            elif '@type' in receipt:
                type = receipt['@type']
            else:
                raise AssertionError("Cannot identify Chainpoint version")

            isValid_type = re.match('^Chainpoint.*v2$', type)  # validate 'type' attribute value
            if isValid_type:
                receipt_version = '2'
            if not receipt_version:
                raise AssertionError("Invalid Chainpoint type - %s" % type)

        if not receipt_version:
            raise ValueError("Cannot identify Chainpoint version")

        if receipt_version == '1.0' or receipt_version == '1.1':
            return self._validate1xReceipt(receipt)
        elif receipt_version == '2':
            return self._validate2xReceipt(receipt, type)
        else:
            raise ValueError('Invalid Chainpoint version - %s' % receipt_version)


    def _guard(self, obj, attr, err_msg):
        if (attr not in obj) or (not obj[attr] and not isinstance(obj[attr], list)):
            raise AssertionError( err_msg )
        return obj[attr]

    def _guard_hash(self, obj, attr, hash_len, err_msg):
        hash =  self._guard(obj, attr, err_msg)
        if not re.match("^[A-Fa-f0-9]{%i}$" % hash_len, hash):
            raise AssertionError("Invalid hash value - %s" % attr)
        return hash

    def _validate1xReceipt(self, receipt):
        receipt_header = self._guard(receipt, 'header', 'Missing header')
        hash_type = self._guard(receipt_header, 'hash_type', 'Missing hash type')

        if hash_type not in self.CHAINPOINTv1_VALID_HASHTYPES:
            raise AssertionError('Invalid hash type - %s' % hash_type)

        tx_id = self._guard_hash(receipt_header, 'tx_id', 64, 'Missing transaction id')
        timestamp = self._guard(receipt_header, 'timestamp', 'Missing timestamp')
        if not isinstance(timestamp, (int, long)):
            raise AssertionError("Invalid timestamp - %s" % timestamp)

        target = self._guard(receipt, 'target', 'Missing target')
        target_hash = self._guard_hash(target, 'target_hash', 64, 'Missing target hash')
        target_proof = self._guard(target, 'target_proof', 'Missing target proof')
        if not isinstance(target_proof, list):
            raise AssertionError("Invalid target_proof - %s" % target_proof)

        last_parent = target_hash

        for proof in target_proof:
            left = self._guard_hash(proof, 'left', 64, 'Invalid proof path - missing left')
            right = self._guard_hash(proof, 'right', 64, 'Invalid proof path - missing right')
            parent = self._guard_hash(proof, 'parent', 64, 'Invalid proof path - missing parent')
            node_hash = hashlib.sha256(left + right).hexdigest()
            if parent != node_hash:
                raise AssertionError("Invalid proof path")

            # check for presence of last parent
            if left != last_parent and right != last_parent:
                raise AssertionError("Invalid proof path")
            else:
                last_parent = parent

        merkle_root = receipt_header['merkle_root']
        if merkle_root != last_parent:
            raise AssertionError("Invalid proof path - merkle root does not match")

        anchor = dict(type= 'BTCOpReturn', source_id= tx_id, merkle_root = merkle_root)
        return anchor


    def _validate2xReceipt(self, receipt, receipt_type):
        context = receipt['@context']
        hash_type_re = re.match('^Chainpoint(.*)v2$', receipt_type)
        if not hash_type_re:
            raise AssertionError("Invalid Chainpoint type - %s" % receipt_type)

        hash_type = hash_type_re.groups()[0]
        if hash_type not in self.CHAINPOINTv2_VALID_HASHTYPES:
            raise AssertionError("Invalid Chainpoint type - %s" % receipt_type)

        hash_type_bits = hash_type[-3:]
        hash_len = (int(hash_type_bits) / 4)
        hash_test_text = "^[A-Fa-f0-9]{%i}$" % hash_len

        target_hash = self._guard_hash(receipt, 'targetHash', hash_len, 'Missing target hash')
        merkle_root = self._guard_hash(receipt, 'merkleRoot', hash_len, 'Missing merkle root')

        proof = self._guard(receipt, 'proof', 'Missing target proof')
        if not proof and target_hash != merkle_root:
            raise AssertionError("Invalid proof path")

        all_valid_hashes = True
        for p in proof:
            if 'left' in p:
                proof_item_value = p['left']
            elif  'right' in p:
                proof_item_value = p['right']
            else:
                raise AssertionError("Invalid proof path")

            if not re.match(hash_test_text, proof_item_value):
                raise AssertionError("Invalid proof path")

        merkle_tools = MerkleTools(hash_type=hash_type)
        isValid = merkle_tools.validate_proof(proof, target_hash, merkle_root)
        if not isValid:
            raise AssertionError("Invalid proof path")

        return True
