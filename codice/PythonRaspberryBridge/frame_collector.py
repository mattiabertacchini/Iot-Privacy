from device_manager import check_working, get_active_devices, streaming_capture, remove_device, rfid_tag_reader
from datetime import datetime
import threading, time

verbose = False

# always active thread to manage device list update
# check_dev_status = threading.Thread(target=check_working_loop)
# check_dev_status.start()

active_thread = {}
while True:
    check_working()
    active_dev_list = get_active_devices()
    if verbose: print("=" * 50)
    if verbose: print(f"Active dev.:\n{active_dev_list}")
    if verbose: print(f"Pool dev.:\n{active_thread}")
    # check all active dev and create thread for the new one
    if verbose: print(datetime.now().strftime("%d/%m/%Y %H:%M"))
    for dev_ip_addr_dict in active_dev_list:

        dev_ip_addr = dev_ip_addr_dict["camera_ip"]
        dev_ip_rfid = dev_ip_addr_dict["rfid_ip"]
        shelf_id = dev_ip_addr_dict["shelf_id"]
        # create new thread
        if dev_ip_addr not in active_thread:
            # old -> check_dev_status = threading.Thread(target=streaming_capture, args=(dev_ip_addr, dev_ip_rfid, shelf_id))
            check_dev_status = threading.Thread(target=rfid_tag_reader, args=(dev_ip_addr, dev_ip_rfid, shelf_id, True))
            active_thread[dev_ip_addr] = check_dev_status
            if verbose: print(f"Process {dev_ip_addr} created...")
            active_thread[dev_ip_addr].start()
            if verbose: print(f"Process {dev_ip_addr} ran...")
            if verbose: print(active_thread)

    # remove all inactive thread
    thread_to_remove = []
    for pool_ip in active_thread:
        if pool_ip not in [diz["camera_ip"] for diz in active_dev_list]:
            if verbose: print(f"Process {pool_ip} aborted...")
            thread_to_remove.append(pool_ip)
            remove_device(pool_ip, "camera")


    for ip in thread_to_remove:
        del active_thread[ip]

    if verbose: print("=" * 50)
    time.sleep(2)
