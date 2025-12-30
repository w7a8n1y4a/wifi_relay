import gc

print('\n')

from wifi_manager import WifiManager

wifi = WifiManager(env_file_path='/env.json')
sta = wifi.get_sta()
wifi.connect_forever(connect_timeout_ms=10000)

gc.collect()

print('free_mem:',  gc.mem_free(), 'alloc_mem:',  gc.mem_alloc())
print('Boot Success')
