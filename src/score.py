class Score:
    def __init__(
        self,
        user: dict,
        score: int,
        accuracy: float,
        pp: float,
        rank: str,
        mods: int,
        max_combo: int,
        count_300: int,
        count_100: int,
        count_50: int,
        count_geki: int,
        count_katu: int,
        count_miss: int,
        time: str,
        play_mode: int,
        completed: int,
        beatmap_md5: str,
        **kwargs
    ):
        self.username = user["username"]
        self.score = score
        self.accuracy = accuracy
        self.pp = pp
        self.rank = rank
        self.mods = mods
        self.max_combo = max_combo
        self.count_300 = count_300
        self.count_100 = count_100
        self.count_50 = count_50
        self.count_geki = count_geki
        self.count_katu = count_katu
        self.count_miss = count_miss
        self.time = time
        self.play_mode = play_mode
        self.completed = completed
        self.beatmap_md5 = beatmap_md5
        self.kwargs = kwargs
