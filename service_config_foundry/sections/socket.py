class Socket:
    def __init__(self):
        self.unit_name = "Socket"
        self.listen_stream = None
        self.listen_datagram = None
        self.listen_sequential_packet = None
        self.listen_f_i_f_o = None
        self.accept = None
        self.socket_user = None
        self.socket_group = None
        self.socket_mode = None
        self.service = None
