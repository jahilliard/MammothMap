import hashlib

class Checksum(object):

    def __init__(self, lift_status):
        self.lift_status = lift_status

    def checksum(self):
        hash_body = ':'.join(map(lambda x: x['status'] + '-' + x['myID'], self.lift_status))
        hl = hashlib.md5()
        hl.update(hash_body.encode(encoding='UTF-8'))
        return hl.hexdigest()
