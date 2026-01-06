import pymem
import pymem.process
import pymem.pattern
from pynput import keyboard
# Keyboard event handlers
def on_press(key):
    try:
        if key == keyboard.Key.space:  # Space increases the value
            print("Space key pressed: Increasing value by 1")
            modify_memory(target_process_name, ypos, 4, data_type)
        elif key == keyboard.Key.ctrl_l:  # Ctrl decreases the value
            print("Ctrl key pressed: Decreasing value by 1")
            modify_memory(target_process_name, ypos, -4, data_type)
        elif key == keyboard.KeyCode.from_char('a'):  # Move left
            print("A key pressed: Increasing value by 1")
            modify_memory(target_process_name, xpos, 4, data_type)
        elif key == keyboard.KeyCode.from_char('d'):  # Move right
            print("D key pressed: Decreasing value by 1")
            modify_memory(target_process_name, xpos, -4, data_type)
        elif key == keyboard.KeyCode.from_char('w'):  # Move up
            print("W key pressed: Increasing value by 1")
            modify_memory(target_process_name, zpos, 4, data_type)
        elif key == keyboard.KeyCode.from_char('s'):  # Move down
            print("S key pressed: Decreasing value by 1")
            modify_memory(target_process_name, zpos, -4, data_type)
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.f4:
        # Stop listener
        print("F4 pressed: Exiting.")
        return False
def modify_memory(pm, target_address, value_change, data_type='int') -> None:
    try:
        # Attach pymem to the target process by its name

        # Assuming the target address is an absolute address
        absolute_address = target_address

        #dadaaas Read current value from memory
        if data_type == 'int':
            current_value = pm.read_int(absolute_address)
            print(f"Current int value at {hex(absolute_address)}: {current_value}")
            new_value = current_value + value_change  # Modify value based on key press
            pm.write_int(absolute_address, new_value)
            print(f"New int value written to {hex(absolute_address)}: {new_value}")
        elif data_type == 'float':
            current_value = pm.read_float(absolute_address)
            print(f"Current float value at {hex(absolute_address)}: {current_value}")
            new_value = current_value + value_change  # Modify value based on key press
            pm.write_float(absolute_address, new_value)
            print(f"New float value written to {hex(absolute_address)}: {new_value}")
        else:
            print("Unsupported data type")

    except pymem.exception.MemoryReadError as e:
        print(f"Memory read error: {e}")
    except pymem.exception.MemoryWriteError as e:
        print(f"Memory write error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if pm:
            pm.close_process()
def modify_memory(process_name, target_address, value_change, data_type='int') -> None:
    try:
        # Attach pymem to the target process by its name
        pm = pymem.Pymem(process_name)

        # Assuming the target address is an absolute address
        absolute_address = target_address

        #dadaaas Read current value from memory
        if data_type == 'int':
            current_value = pm.read_int(absolute_address)
            print(f"Current int value at {hex(absolute_address)}: {current_value}")
            new_value = current_value + value_change  # Modify value based on key press
            pm.write_int(absolute_address, new_value)
            print(f"New int value written to {hex(absolute_address)}: {new_value}")
        elif data_type == 'float':
            current_value = pm.read_float(absolute_address)
            print(f"Current float value at {hex(absolute_address)}: {current_value}")
            new_value = current_value + value_change  # Modify value based on key press
            pm.write_float(absolute_address, new_value)
            print(f"New float value written to {hex(absolute_address)}: {new_value}")
        else:
            print("Unsupported data type")

    except pymem.exception.MemoryReadError as e:
        print(f"Memory read error: {e}")
    except pymem.exception.MemoryWriteError as e:
        print(f"Memory write error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if pm:
            pm.close_process()

def create_car_list(pm,address) -> list[int]:
    cars = []
    i = 0
    while i < 0xffc:
        try:
            addr = pm.read_int(address + i)
            if pm.read_int(addr) == 0x64bcd0:
                print(f"[*] car found! {hex(addr)}")
                cars.append(addr)
        except:
            pass
        i+=0x04
    return cars

def fly():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
def enable_bonuses(pm,process_name,car_addr):
    bonus_addr = pm.read_int(car_addr + 0x190)
    print(hex(bonus_addr))
    try:
        if pm.read_int(bonus_addr) == 0x64c07c:
            for i in range(12):
                bonus = bonus_addr+0x0b0+(0x88*i)
                print(hex(bonus))
                modify_memory(process_name=process_name,target_address=bonus,value_change=99999,data_type='int')
    except:
        print("[!] couldnt enable bonuses")

def main():
    game_addr = 0x400000
    offset = 0x28d9fc
    global target_process_name,xpos,ypos,zpos,data_type
    target_process_name = "MadTracks.exe"

    pm = pymem.Pymem(target_process_name)
    module = pymem.process.module_from_name(pm.process_handle, target_process_name)
    base_address = module.lpBaseOfDll
    memory_size = module.SizeOfImage

    first_pointer = pm.read_int(game_addr+offset)
    second_pointer = pm.read_int(first_pointer + 0x20c)
    entity_list = pm.read_int(second_pointer + 0xc)
    car_list = create_car_list(pm,entity_list)
    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            if len(car_list) != 0:
                player_car = car_list[0]
                enable_bonuses(pm,target_process_name,player_car)
                xpos = player_car + 0x38
                ypos = player_car + 0x3c
                zpos = player_car + 0x40
                print(hex(xpos),hex(ypos),hex(zpos))
                data_type = "float"
                listener.join()

if __name__ == "__main__":
    main()
