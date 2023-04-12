import itertools
import json
import pickle
from dataclasses import dataclass, field
from typing import List


class History:
    def __init__(self, app):
        self.app = app

    def get(self, redis, user):
        hist = redis.get(user)
        if not hist:
            return []
        return self.from_bytes(hist)

    def set(self, redis, user, instance):
        hist = redis.get(user)
        if not hist:
            hist = [instance]
        else:
            hist = self.from_bytes(hist)
            hist.append(instance)
        redis.set(user, self.to_bytes(hist))

    def delete(self, redis, user):
        redis.set(user, self.to_bytes([]))

    def to_bytes(self, instance):
        return pickle.dumps(instance)

    def from_bytes(self, bts):
        return pickle.loads(bts)
