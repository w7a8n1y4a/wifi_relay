import time
import network
import ujson as json


class WifiManager:
    DEBUG_PREFIX = "Network Debug:"

    def __init__(self, env_file_path="/env.json"):
        self.env_file_path = env_file_path
        self.env = self._read_env(env_file_path)
        self.ssid = self.env.get("WIFI_SSID", "") or ""
        self.password = self.env.get("WIFI_PASS", "") or ""
        self.max_reconnection_interval = int(self.env.get("MAX_RECONNECTION_INTERVAL", 60000))

        self._sta = None

    def debug(self, text):
        print(self.DEBUG_PREFIX, text)

    def get_sta(self):
        if self._sta is None:
            sta = network.WLAN(network.STA_IF)
            if not sta.active():
                sta.active(True)
            self._sta = sta
        return self._sta

    def is_connected(self):
        return bool(self.get_sta().isconnected())

    def scan_has_target_ssid(self):
        sta = self.get_sta()
        scan = sta.scan()
        for ap in scan:
            ap_ssid = ap[0]
            if isinstance(ap_ssid, bytes):
                try:
                    ap_ssid = ap_ssid.decode()
                except Exception:
                    ap_ssid = ""
            if ap_ssid == self.ssid:
                return True
        return False

    def connect_once(self, timeout_ms=10000):
        sta = self.get_sta()

        if sta.isconnected():
            return True

        if not self.ssid:
            self.debug("WIFI_SSID is empty; can't connect")
            return False

        sta.connect(self.ssid, self.password)

        started = time.ticks_ms()
        while not sta.isconnected():
            if time.ticks_diff(time.ticks_ms(), started) >= int(timeout_ms):
                return False
            time.sleep_ms(200)

        return True

    def connect_forever(self, connect_timeout_ms=10000):
        attempt = 0
        while True:
            if self.is_connected():
                try:
                    self.debug("connected: " + str(self.get_sta().ifconfig()))
                except Exception:
                    self.debug("connected")
                return True

            wait_ms = self._reconnection_interval_ms(attempt)

            try:
                if self.scan_has_target_ssid():
                    ok = self.connect_once(timeout_ms=connect_timeout_ms)
                    if ok:
                        continue
                    self.debug("connect timeout; next try in {} ms".format(wait_ms))
                else:
                    self.debug('ssid "{}" not found; next scan in {} ms'.format(self.ssid, wait_ms))
            except Exception as e:
                self.debug("wifi error: " + str(e) + "; next try in {} ms".format(wait_ms))

            if wait_ms > 0:
                time.sleep_ms(wait_ms)
            attempt += 1

    def ensure_connected(self):
        if not self.is_connected():
            return self.connect_forever()
        return True

    def _reconnection_interval_ms(self, attempt):
        if attempt <= 0:
            return 0
        base = 5000
        interval = base * (2 ** (attempt - 1))
        if interval > self.max_reconnection_interval:
            return self.max_reconnection_interval
        return int(interval)

    @staticmethod
    def _read_env(path):
        try:
            with open(path, "r") as f:
                return json.load(f) or {}
        except Exception:
            return {}
