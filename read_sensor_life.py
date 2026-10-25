import spidev
import sys
import time

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000


def read_channel(data):
    # xfer2 keeps CS active across the entire 3-byte payload
    adc = spi.xfer2([1, (8 + data) << 4, 0])
    data_ = ((adc[1] & 3) << 8) + adc[2]
    return data_


def read_data():
    channel_data_dic = {0: [], 1: [], 2: []}

    # Takes 10 readings across 0.5 seconds
    for x in range(10):
        for i in range(3):
            channel_data_dic[i].append(read_channel(i))
        time.sleep(0.05)

    # Return averaged values
    return {
        ch: sum(vals) / len(vals) for ch, vals in channel_data_dic.items()
    }


if __name__ == "__main__":
    print("Continuously reading MCP3008 (Channels 0-2). Press Ctrl+C to stop.\n")

    try:
        while True:
            averages = read_data()

            # Format the output on a single line
            output_str = (
                f"\rCH 0: {averages[0]:6.1f} | "
                f"CH 1: {averages[1]:6.1f} | "
                f"CH 2: {averages[2]:6.1f}"
            )

            # \r moves the cursor back to the line start; flush forces immediate output
            sys.stdout.write(output_str)
            sys.stdout.flush()

            # Wait 0.5s (0.5s sampling + 0.5s sleep = 1.0s update rate)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\nStopping script...")
    finally:
        spi.close()
