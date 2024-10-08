from api_play import APIPlay

class APIPong(APIPlay) :

    def __init__(self) :
        super().__init__()

    def get_pong_ws_url(self) :
        return self.get_base_url('ws') + "pong/" + str(self.match_choice_id) if self.match_choice_id else ""