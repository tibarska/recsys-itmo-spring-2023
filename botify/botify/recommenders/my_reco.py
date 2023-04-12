from .random import Random
from .recommender import Recommender
import random
from typing import List
from .toppop import TopPop
from .indexed import Indexed
from .contextual import Contextual


class My_Reco(Recommender):
    """ Version of neuro recommender/ Should be improved"""
    def __init__(self, tracks_redis, history_redis, history, recommendations_redis, catalog, top_tracks: List[int]):
        self.tracks_redis = tracks_redis
        self.history_redis = history_redis
        self.history = history
        self.fallback = Indexed(tracks_redis, recommendations_redis, catalog)
        self.second_fallback = Contextual(tracks_redis, catalog)
        self.catalog = catalog
        self.top_tracks = top_tracks
        self.top_dict = {track: rating for (rating, track) in enumerate(top_tracks)}
        self.user_history = {}

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        user_history = set(self.history.get(self.history_redis, user))
        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:  # у юзера нет истории
            track_to_listen = self.fallback.recommend_next(user, prev_track, prev_track_time)
            self.history.set(self.history_redis, user, track_to_listen)
            return track_to_listen

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations


        if recommendations is None:
            track_to_listen = self.fallback.recommend_next(user, prev_track, prev_track_time)
            self.history.set(self.history_redis, user, track_to_listen)
            return track_to_listen

        shuffled = set(recommendations)
        shuffled = list(shuffled.difference(user_history))
        if self.top_tracks and shuffled:
            shuffled_top = [self.top_dict.get(track, 50000) for track in shuffled]
            rec_dict = {track: top for (track, top) in zip(shuffled, shuffled_top)}
            sorted_rec_dict = {k: v for k, v in sorted(rec_dict.items(), key=lambda item: item[1])}
            sorted_rec_list = list(sorted_rec_dict.keys())[:50]
            random.shuffle(sorted_rec_list)
            track_to_listen = sorted_rec_list[0]
            self.history.set(self.history_redis, user, track_to_listen)
            return track_to_listen

        elif shuffled:
            random.shuffle(shuffled)
            track_to_listen = shuffled[0]
            self.history.set(self.history_redis, user, track_to_listen)

        track_to_listen = self.fallback.recommend_next(user, prev_track, prev_track_time)
        self.history.set(self.history_redis, user, track_to_listen)
        return track_to_listen
