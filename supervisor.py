import time

from pepeunit_micropython_client.settings import Settings
from pepeunit_micropython_client.logger import Logger
from pepeunit_micropython_client.time_manager import TimeManager


class Supervisor:
    def __init__(self, env_path='/env.json', log_path='/log.json'):
        self.env_path = env_path
        self.log_path = log_path

        self.settings = Settings(env_path)
        self.time_manager = TimeManager()
        self.logger = Logger(log_path, None, None, self.settings, self.time_manager)

        self.reconnect_delay_ms = 0

    def next_backoff_ms(self, current_ms):
        
        if current_ms == 0:
            target_ms = 5000
        if current_ms >= 5000:
            target_ms = current_ms * 2
        if target_ms > self.settings.MAX_RECONNECTION_INTERVAL:
            target_ms = self.settings.MAX_RECONNECTION_INTERVAL

        return target_ms

    def _ensure_wifi_connected(self, sta, ssid, password, attempt_timeout_ms=10000):
        print('test')
        if sta is None:
            return False

        try:
            if not sta.active():
                sta.active(True)
            if sta.isconnected():
                return True
            try:
                sta.disconnect()
            except Exception:
                pass
            sta.connect(ssid, password)
        except Exception:
            return False

        t0 = time.ticks_ms()
        while True:
            try:
                if sta.isconnected():
                    return True
            except Exception:
                pass
            if time.ticks_diff(time.ticks_ms(), t0) >= attempt_timeout_ms:
                return False
            time.sleep(0.2)

    def wifi_watchdog(self, client, state, interval_ms=1000):
        now = client.time_manager.get_epoch_ms()
        last = state.get('last_wifi_check_ms', 0)
        if (now - last) < interval_ms:
            return
        state['last_wifi_check_ms'] = now

        if client.sta is None:
            return
        if not client.sta.isconnected():
            raise RuntimeError('wifi_disconnected')

    def run_forever(self, main_fn, sta):
        while True:
            self.settings.load_from_file()

            ssid = getattr(self.settings, 'WIFI_SSID', '')
            password = getattr(self.settings, 'WIFI_PASS', '')

            if self.reconnect_delay_ms > 0:
                time.sleep(self.reconnect_delay_ms / 1000)

            if not self._ensure_wifi_connected(sta, ssid, password, attempt_timeout_ms=10000):
                self.reconnect_delay_ms = self.next_backoff_ms(self.reconnect_delay_ms)
                print('fail', self.reconnect_delay_ms)
                self.logger.warning(
                    'WiFi connect failed. Next reconnect in {} ms'.format(self.reconnect_delay_ms),
                    file_only=True,
                )
                continue

            try:
                self.reconnect_delay_ms = 0
                main_fn(sta)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.logger.critical(f'Unit crash: {str(e)}', file_only=True)
                self.reconnect_delay_ms = self.next_backoff_ms(self.reconnect_delay_ms)
