"""!sysinfo use psutil to get system information"""
from datetime import datetime
import psutil
from psutil._common import bytes2human
from pyrogram import Client, filters

self_or_contact_filter = filters.create(
    lambda
    _,
    __,
    message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)


async def generate_sysinfo(workdir):
    # uptime
    info = {}
    info['boot'] = (
        datetime
        .fromtimestamp(psutil.boot_time())
        .strftime("%Y-%m-%d %H:%M:%S")
    )
    # CPU
    cpu_freq = psutil.cpu_freq().current
    if cpu_freq >= 1000:
        cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
    else:
        cpu_freq = f"{round(cpu_freq, 2)}MHz"
    info['cpu'] = (
        f"{psutil.cpu_percent(interval=1)}% "
        f"({psutil.cpu_count()}) "
        f"{cpu_freq}"
    )
    # Memory
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    info['ram'] = (f"{bytes2human(vm.total)}, "
                   f"{bytes2human(vm.available)} available")
    info['swap'] = f"{bytes2human(sm.total)}, {sm.percent}%"
    # Disks
    du = psutil.disk_usage(workdir)
    dio = psutil.disk_io_counters()
    info['disk'] = (f"{bytes2human(du.used)} / {bytes2human(du.total)} "
                    f"({du.percent}%)")
    if dio:
        info['disk io'] = (f"R {bytes2human(dio.read_bytes)} | "
                           f"W {bytes2human(dio.write_bytes)}")
    # Network
    nio = psutil.net_io_counters()
    info['net io'] = (f"TX {bytes2human(nio.bytes_sent)} | "
                      f"RX {bytes2human(nio.bytes_recv)}")
    # Sensors
    sensors_temperatures = psutil.sensors_temperatures()
    if sensors_temperatures:
        temperatures_list = [
            x.current
            for x in sensors_temperatures['coretemp']
        ]
        temperatures = sum(temperatures_list) / len(temperatures_list)
        info['temp'] = f"{temperatures}\u00b0C"
    info = {f"{key}:": value for (key, value) in info.items()}
    max_len = max(len(x) for x in info)
    return (
        "```"
        + "\n".join([f"{x:<{max_len}} {y}" for x, y in info.items()])
        + "```"
    )
    """
    partition_info = []
    for part in psutil.disk_partitions():
        mp = part.mountpoint
        du = psutil.disk_usage(mp)
        partition_info.append(f"{part.device} {mp} "
                              f"{part.fstype} "
                              f"{du.used} / {du.total} {du.percent}")
    partition_info = ",".join(partition_info)
    """


@Client.on_message(filters.group
                   & filters.text
                   & self_or_contact_filter
                   & ~filters.edited
                   & ~filters.via_bot
                   & filters.regex("^!sysinfo$"))
async def get_sysinfo(client, m):
    response = "**System Information**:\n"
    m_reply = await m.reply_text(f"{response}`...`")
    response += await generate_sysinfo(client.workdir)
    await m_reply.edit_text(response)
