import click
import time
import subprocess
from subprocess import PIPE, STDOUT, DEVNULL
import helper as hp


@click.group()
def cli():
    pass


@cli.command(help="Start IoT lab environment, option: --scale-esp32 n")
@click.option("--scale-esp32", default=1)
def start(scale_esp32):
    subprocess.Popen(
        [
            "docker-compose",
            "up",
            "--scale",
            "esp32-dev={}".format(str(scale_esp32)),
        ],
        stdin=PIPE,
        stdout=DEVNULL,
        stderr=STDOUT,
    )
    click.echo("Starting IoT Lab, please wait!")
    time.sleep(15)

    raspberry_pi_id = hp.get_raspberry_pi_device_id()
    if raspberry_pi_id:
        click.echo(
            "IoT lab started. 1 instance of ESP32 and {} instance of Raspberry Pi are running!".format(
                scale_esp32
            )
        )
    else:
        click.echo("IoT lab couldn't be started!")


@cli.command(help="Stop IoT lab environment")
def stop():
    raspberry_pi_id = hp.get_raspberry_pi_device_id()
    if raspberry_pi_id:
        subprocess.run(["docker-compose", "down"], stderr=STDOUT)

        click.echo("IoT Lab stopped!")
    else:
        click.echo("IoT Lab is not running!")


@cli.command(help="Restart IoT lab environment")
@click.pass_context
def restart(context):
    context.invoke(stop)
    context.invoke(start)

@cli.command(help="Start Arduino environment")
def arduino():
    subprocess.run(["docker", "exec", "-it", "esp32-qemu", "/usr/local/bin/arduino"], stderr=STDOUT)
    #subprocess.run(["/usr/bin/xhost", "+'LOCAL:docker@';", "sudo", "docker", "exec", "-it", "esp32-qemu", "/usr/local/bin/arduino"], shell=True, stderr=STDOUT)
    click.echo("Arduino environment started!")

@cli.command(help="Generate bin from workspace")
def generatebin():
    #output=subprocess.run("/usr/bin/pwd", "| /usr/bin/awk", "'{split($0,a,\"/esp32-qemu/workspace/\"); print a[2]}'", capture_output=True)
    subprocess.run("""tmp=`/usr/bin/pwd | /usr/bin/awk '{split($0,a,\"/esp32-qemu/workspace/\"); print a[2]}' | sed 's/\\n//g'`;
                        docker exec -it esp32-qemu bash -c 'cd /root/workspace/'${tmp}'; /esp32-bin/make-flash-img.sh'""", capture_output=False, shell=True)
    #                    sudo docker exec -it esp32-qemu bash -c cd /root/workspace/${tmp}; /esp32-bin/make-flash-img.sh""",capture_output=True, shell=True,text=True)
    #directory = output.stdout or ";"
    #print(directory)
    #subprocess.run(["sudo", "docker", "exec", "-it", "esp32-qemu", "bash", "-c", "cd /root/workspace/" + directory + "; /esp32-bin/make-flash-img.sh"], stderr=STDOUT)
    #subprocess.run(["/usr/bin/xhost", "+'LOCAL:docker@';", "sudo", "docker", "exec", "-it", "esp32-qemu", "/usr/local/bin/arduino"], shell=True, stderr=STDOUT)
    click.echo("Bin generation finished!")

@cli.command(help="['esp32 --id [1 to n]', 'raspberry_pi'] device logs")
@click.argument("device")
@click.option("--id")
def log(device, id):
    if device == "raspberry_pi":
        device_id = hp.get_raspberry_pi_device_id()
        subprocess.run(["docker", "logs", device_id])
    elif device == "esp32":
        if id:
            device_id = hp.get_esp32_device_id(id)
            subprocess.run(["docker", "logs", device_id])
        else:
            click.echo("Provide ESP32 device id")
    else:
        click.echo("Please provide one of [esp32, raspberry_pi]")


@cli.command(help="Same as idf.py flash, option: --id n")
@click.option("--id")
def flash(id):
    device_id = hp.get_esp32_device_id(id)
    device_port = hp.get_esp32_port(id, type="flash")
    print("Device port: " + str(device_port))
    if not device_port:
        click.echo("No ESP32 device found with id {}".format(id))
        return
    subprocess.run(
        [
            "docker",
            "exec",
            device_id,
            "bash",
            "-c",
            "pkill -f qemu-system-xtensa",
        ],
        stdout=DEVNULL,
        stderr=STDOUT,
    )
    subprocess.Popen(
        [
            "docker",
            "exec",
            device_id,
            "bash",
            "-c",
            "/qemu-system-xtensa/qemu-system-xtensa -nographic -machine esp32 -drive file=flash_image.bin,if=mtd,format=raw -global driver=esp32.gpio,property=strap_mode,value=0x0f -echr 0x02 -serial tcp::5555,server -nic user,model=open_eth,id=lo0,hostfwd=tcp::3333-:3333 -gdb tcp::1234",
        ],
        stdout=DEVNULL,
        stderr=STDOUT,
    )
    subprocess.run("""tmp=`/usr/bin/pwd | /usr/bin/awk '{split($0,a,"/esp32-qemu/workspace/"); print a[2]}'`;
                        docker exec -it esp32-qemu bash -c 'cd /root/workspace/'${tmp}'; /esp32-qemu/esp/esp-idf/tools/idf.py flash -p socket://esp32-dev:""" + device_port + "'", capture_output=False, shell=True)

    #subprocess.run("sudo docker exec -it esp32-qemu bash -c 'cd /root/workspace/current; /esp32-qemu/esp/esp-idf/tools/idf.py flash -p socket://esp32-dev:{}'".format(device_port), capture_output=False, shell=True)

#    subprocess.run(
#        ["docker", "exec", "-it", "esp32-qemu", "cd /root/workspace/current;", "/esp32-qemu/esp/esp-idf/tools/idf.py", "flash", "-p", "socket://localhost:{}".format(device_port)]
#    )


@cli.command(help="Same as idf.py monitor, option: --id n")
@click.option("--id")
def monitor(id):
    device_id = hp.get_esp32_device_id(id)
    device_port = hp.get_esp32_port(id, type="monitor")

    if not device_port:
        click.echo("No ESP32 device found with id {}".format(id))
        return
    subprocess.run(
        [
            "docker",
            "exec",
            device_id,
            "bash",
            "-c",
            "killall qemu-system-xtensa",
        ]
    )
    subprocess.Popen(
        [
            "docker",
            "exec",
            device_id,
            "bash",
            "-c",
            "./qemu-system-xtensa/qemu-system-xtensa -nographic -machine esp32 -drive file=flash_image.bin,if=mtd,format=raw -echr 0x02 -serial tcp::5555,server -nic user,model=open_eth,id=lo0,hostfwd=tcp::3333-:3333 -gdb tcp::1234",
        ],
        stdout=DEVNULL,
        stderr=STDOUT,
    )
    subprocess.run(
        #["docker exec -it esp32-qemu /esp32-qemu/esp/esp-idf/tools/idf.py", "monitor", "-p", "socket://localhost:{}".format(device_port)]
        ["docker", "exec", "-it", "esp32-qemu", "/esp32-qemu/esp/esp-idf/tools/idf.py","monitor", "-p", "socket://localhost:{}".format(device_port)]
    )


@cli.command(help="See raspberry pi gpio state")
def rgpio():
    device_id = hp.get_raspberry_pi_device_id()
    if not device_id:
        click.echo("No Raspberry Pi device found")
        return
    subprocess.run(
        [
            "docker",
            "exec",
            "-t",
            device_id,
            "/usr/local/bin/detect_gpio_changes",
        ],
    )


@cli.command(help="SSH into raspbian")
def ssh():
    subprocess.run(
        [
            "ssh",
            "-p",
            "2222",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "StrictHostKeyChecking=no",
            "pi@localhost",
        ]
    )


@cli.command(help="Get port information of ESP32, option: --id n")
@click.option("--id")
def eport(id):
    flash_or_monitor_port = hp.get_esp32_port(id, type="flash")
    socket_port = hp.get_esp32_port(id, type="socket")
    gdb_port = hp.get_esp32_port(id, type="gdb")

    click.echo("flash or monitor port: {}".format(flash_or_monitor_port))
    click.echo("socket port: {}".format(socket_port))
    click.echo("GDB port: {}".format(gdb_port))


@cli.command(help="Connect to socket port of ESP32, option: --id n")
@click.option("--id")
def esocket(id):
    socket_port = hp.get_esp32_port(id, type="socket")
    if not socket_port:
        click.echo("ESP32 socket port counldn't be found")
    subprocess.run(["nc", "localhost", socket_port])
