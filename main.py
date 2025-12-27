import time
import machine
import ujson as json

from pepeunit_micropython_client.client import PepeunitClient
from pepeunit_micropython_client.enums import SearchTopicType, SearchScope


last_command_state_update_time = 0
last_output_send_time = 0
last_command = None
target_command = None

pwm = None
force_activation_pin = None
force_deactivation_pin = None

active_action = None
scheduled_timer = None

def init_pins(client):
    global pwm, force_activation_pin, force_deactivation_pin

    pwm = machine.PWM(machine.Pin(int(client.settings.PIN_RELAY)), freq=int(client.settings.PIN_RELAY_PWM_FREQUENCY), duty_u16=0)
    force_activation_pin = machine.Pin(int(client.settings.PIN_FORCE_ACTIVATION), machine.Pin.IN, machine.Pin.PULL_UP)
    force_deactivation_pin = machine.Pin(int(client.settings.PIN_FORCE_DEACTIVATION), machine.Pin.IN, machine.Pin.PULL_UP)


def output_handler(client: PepeunitClient):
    global last_command_state_update_time, last_output_send_time
    global pwm, last_command, target_command, active_action, scheduled_timer

    current_time = client.time_manager.get_epoch_ms()

    # publish last command
    if (current_time - last_output_send_time) >= client.settings.PUBLISH_SEND_INTERVAL:
        client.publish_to_topics('last_command/pepeunit', json.dumps(last_command))
        client.logger.debug('last_command: ' + json.dumps(last_command), file_only=True)

        last_output_send_time = current_time

    # non-blocking scheduled timer start
    if isinstance(scheduled_timer, dict) and current_time >= scheduled_timer.get('time_run', 0):
        duty = scheduled_timer.get('target_duty', 0)
        duration = scheduled_timer.get('duration', 0)
        pwm.duty_u16(duty)
        active_action = {
            'kind': 'timer',
            'end_time': current_time + duration,
        }
        scheduled_timer = None

    # non-blocking timed action stop
    if isinstance(active_action, dict) and current_time >= active_action.get('end_time', 0):
        pwm.duty_u16(0)
        active_action = None

    # command execution
    if (current_time - last_command_state_update_time) >= 50:
        if target_command is not None:
            last_command = target_command
            target_command = None

            command_type = last_command.get('command_type')
            target_duty = int(last_command.get('target_duty', 0))
            duration = int(last_command.get('duration', 0))
            time_run = int(last_command.get('time_run', 0))
            
            active_action = None
            scheduled_timer = None
            if command_type == 'set':
                pwm.duty_u16(int(target_duty))

            elif command_type == 'duration':
                pwm.duty_u16(int(target_duty))
                active_action = {
                    'kind': 'duration',
                    'end_time': current_time + duration,
                }
            elif command_type == 'timer':
                scheduled_timer = {
                    'kind': 'timer',
                    'time_run': time_run,
                    'duration': duration,
                    'target_duty': int(target_duty),
                }

        last_command_state_update_time = current_time

def input_handler(client: PepeunitClient, msg):
    global target_command

    parts = msg.topic.split('/')

    if len(parts) == 3:
        topic_name = client.schema.find_topic_by_unit_node(parts[1], SearchTopicType.UNIT_NODE_UUID, SearchScope.INPUT)

        if topic_name == 'relay_command/pepeunit':
            client.logger.info('Get command from mqtt: ' + str(msg.payload))
            target_command = json.loads(msg.payload)
            target_command['time'] = client.time_manager.get_epoch_ms()


def main():
    client = PepeunitClient(
        env_file_path='/env.json',
        schema_file_path='/schema.json',
        log_file_path='/log.json',
        sta=sta
    )
    client.set_mqtt_input_handler(input_handler)
    client.mqtt_client.connect()
    client.subscribe_all_schema_topics()
    client.set_output_handler(output_handler)

    init_pins(client)

    client.run_main_cycle()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        try:
            print('Error:', str(e))
        except Exception:
            pass
