import pymem
import pymem.process
import time as t
from pynput import keyboard
import customtkinter as ctk

# Keyboard event handlers
def on_press(key):
    try:
        if key == keyboard.Key.space:  # Space increases the value
            print("Space key pressed: Increasing value by 1")
            modify_memory(process_name=target_process_name, target_address=ypos,value_change=4,data_type=data_type)
        elif key == keyboard.Key.ctrl_l:  # Ctrl decreases the value
            print("Ctrl key pressed: Decreasing value by 1")
            modify_memory(process_name=target_process_name, target_address=ypos,value_change=-4,data_type=data_type)
        elif key == keyboard.KeyCode.from_char('a'):  # Move left
            print("A key pressed: Increasing value by 1")
            modify_memory(process_name=target_process_name, target_address=xpos,value_change=4,data_type=data_type)
        elif key == keyboard.KeyCode.from_char('d'):  # Move right
            print("D key pressed: Decreasing value by 1")
            modify_memory(process_name=target_process_name, target_address=xpos,value_change=-4,data_type=data_type)
        elif key == keyboard.KeyCode.from_char('w'):  # Move up
            print("W key pressed: Increasing value by 1")
            modify_memory(process_name=target_process_name, target_address=zpos,value_change=4,data_type=data_type)
        elif key == keyboard.KeyCode.from_char('s'):  # Move down
            print("S key pressed: Decreasing value by 1")
            modify_memory(process_name=target_process_name, target_address=zpos,value_change=-4,data_type=data_type)
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.f4:
        # Stop listener
        print("F4 pressed: Exiting.")
        return False

def modify_memory(pm=None, process_name=None , target_address=None, value_change=None, data_type='int') -> None:
    created_pm = False
    try:
        # Attach pymem to the target process by its name
        if pm is None:
            pm = pymem.Pymem(process_name)
            created_pm = True

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
        if created_pm and pm:
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

def start_fly():
    global listener
    if listener is None:
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()  # nie blokuje GUI
        print("[*] Flying teleport started")

def stop_fly():
    global listener
    if listener is not None:
        listener.stop()   # można wywołać z dowolnego miejsca
        listener = None
        print("[*] Flying teleport ended")
def enable_bonuses(pm,car_addr):
    global car_bonus_list
    if car_bonus_list is None:
        car_bonus_list = []
        print("[*] Bonuses started")
        bonus_addr = pm.read_int(car_addr + 0x190)
        print(hex(bonus_addr))
        try:
            if pm.read_int(bonus_addr) == 0x64c07c:
                for i in range(12):
                    bonus = bonus_addr+0x0b0+(0x88*i)
                    print(hex(bonus))
                    car_bonus_list.append(pm.read_int(bonus))
                    pm.write_int(bonus,99999)
            print(car_bonus_list)
        except Exception as e:
            print("[!] couldnt enable bonuses")
            print(e)

def disable_bonuses(pm,car_addr):
    bonus_addr = pm.read_int(car_addr + 0x190)
    try:
        if pm.read_int(bonus_addr) == 0x64c07c:
            for i in range(12):
                bonus = bonus_addr+0x0b0+(0x88*i)
                pm.write_int(bonus,car_bonus_list[i])
        print("[*] Bonuses disabled")
    except:
        print("[!] couldnt enable bonuses")
def teleport_through_checkpoints(pm,process_name,entity_list,player):
    print("[*] Checkpoint teleport started")
    checkpoint_list = []
    i = 0
    while i < 0xffc:
        try:
            addr = pm.read_int(entity_list + i)
            if pm.read_int(addr) == 0x64d2a8:
                print(f"[*] checkpoint found! {hex(addr)}")
                checkpoint_list.append(addr)
        except Exception as e:
            pass
        i+=0x04
    for _ in range(20):
        for checkpoint_addr in checkpoint_list:
            #print(f"Checkpoint: {hex(checkpoint_addr)}")
            pm.write_float(player+0x38,pm.read_float(checkpoint_addr+0x38))
            pm.write_float(player+0x3c,pm.read_float(checkpoint_addr+0x3c))
            pm.write_float(player+0x40,pm.read_float(checkpoint_addr+0x40))
            t.sleep(0.01)
    print("[*] Checkpoint teleport ended")

def stuck_bots(pm,cars):
    if len(cars) > 1:
        while True:
            for i in range(1,len(cars)):
                pm.write_float(cars[i]+0x38,pm.read_float(cars[i]+0x38))
                pm.write_float(cars[i]+0x3c,pm.read_float(cars[i])+0x3c)
                pm.write_float(cars[i]+0x40,pm.read_float(cars[i]+0x40))
                t.sleep(0.01)




def main():
    
    WINDOW_SIZE = "320x240"
    FONT = ("Arial",12)

    offset = 0x28d9fc
    global target_process_name,xpos,ypos,zpos,data_type,listener,car_bonus_list,teleport_boolean
    listener,car_bonus_list = None,None

    target_process_name = "MadTracks.exe"

    pm = pymem.Pymem(target_process_name)
    module = pymem.process.module_from_name(pm.process_handle, target_process_name)
    game_addr = module.lpBaseOfDll

    first_pointer = pm.read_int(game_addr+offset)
    second_pointer = pm.read_int(first_pointer + 0x20c)
    entity_list = pm.read_int(second_pointer + 0xc)
    car_list = create_car_list(pm,entity_list)

    player_car = car_list[0]
    xpos = player_car + 0x38
    ypos = player_car + 0x3c
    zpos = player_car + 0x40
    data_type = "float"
    
    print(f"first_pointer= {hex(first_pointer)}")
    print(f"second_pointer={hex(second_pointer)}")
    print(f"entity_list={hex(entity_list)}")

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    app.title("Mad Tracks Cheats by Cappybara")
    app.geometry(WINDOW_SIZE)

    frame = ctk.CTkFrame(app)
    frame.pack(pady=20,padx=20,fill="both",expand=True)

    def toggle_fly():
        if checkbox_fly.get():
            start_fly()
        else:
            stop_fly()

    checkbox_fly = ctk.CTkCheckBox(frame,text="Fly Mode - Move with W,A,S,D,Space,Ctrl",font=FONT,command=toggle_fly)
    checkbox_fly.pack(anchor="w",pady=10)

    def toggle_bonuses():
        if checkbox_bonus.get():
            enable_bonuses(pm,player_car)
        else:
            disable_bonuses(pm,player_car)

    checkbox_bonus = ctk.CTkCheckBox(frame,text="Bonus Hack - Enables all bonuses",font=FONT,command=toggle_bonuses)
    checkbox_bonus.pack(anchor="w",pady=10)
    
    def toggle_teleport_checkpoint():
        teleport_through_checkpoints(pm=pm,process_name=target_process_name,entity_list=entity_list,player=player_car)
    checkpoint_teleport = ctk.CTkButton(frame,text="Checkpoint Hack",font=FONT,command=toggle_teleport_checkpoint)
    checkpoint_teleport.pack(anchor="w",pady=10)

    def toggle_stuck_bots():
        stuck_bots(pm=pm,cars=car_list)
    checkpoint_stuck_bots = ctk.CTkButton(frame,text="Stuck Bots",font=FONT,command=toggle_stuck_bots)
    checkpoint_stuck_bots.pack(anchor="w",pady=10)
    
    app.mainloop()
    

if __name__ == "__main__":
    main()
