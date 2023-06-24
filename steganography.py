from PIL import Image
import cv2
import numpy as np
import os
import time

cwd = os.getcwd()


def print_with_empty_line(*args, **kwargs):
    print()
    print(*args, **kwargs)


class Encode:
    def message_to_binary(message):
        print_with_empty_line("Converting message to binary...")
        message_binary = []
        for char in message:
            message_binary.append(format(ord(char), "08b"))
        return "".join(message_binary)

    def image_to_binary(image_path):
        print_with_empty_line("Converting image to binary...")
        image = Image.open(image_path).convert("RGB")
        image_np = np.array(image)
        image_binary = []
        count = 0
        for index, pixel in np.ndenumerate(image_np):
            if count != int(index[0]):
                image_binary.append(
                    "".join(format(ord(char), "08b") for char in "null")
                )
            image_binary.append(format(pixel, "08b"))
            count = int(index[0])
        return "".join(image_binary)

    def encode_to_image(image_path, data, choice):
        print_with_empty_line("Embedding data into image...")
        host_image = Image.open(image_path).convert("RGB")
        host_image_np = np.array(host_image)
        pixel_array = []
        rgb = ()
        count = 0

        for pixel in np.nditer(host_image_np):
            binary = list(format(pixel, "08b"))
            if not count >= len(data):
                binary[-1] = data[count]
            else:
                binary[-1] = "0"
            rgb += (int("".join(binary), 2),)
            count += 1
            if len(rgb) >= 3:
                pixel_array.append(rgb)
                rgb = ()
        names = ["txt", "img", "multi_img"]
        host_image.putdata(pixel_array)
        host_image_name = f"{names[choice - 1]}_{os.path.basename(image_path)}"
        output_path = os.path.join(cwd, "encoded", host_image_name)
        host_image.save(output_path, "PNG")
        print_with_empty_line("- Successfully embedded data into image.")
        print_with_empty_line("- Image saved as encoded/", host_image_name)

    def encode_to_video(video_path, data, choice):
        print_with_empty_line("Embedding data into video...")
        video = cv2.VideoCapture(video_path)

        if not video.isOpened():
            print_with_empty_line("Error opening video file.")
            exit()

        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        names = ["txt", "img"]
        output_path = os.path.join(cwd, "videos", f"{names[choice - 4]}_output_video.avi")
        fourcc = cv2.VideoWriter_fourcc(*"FFV1")
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        count = 0

        for frame_number in range(total_frames):
            ret, frame = video.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

            frame_np = np.array(frame)

            for index, pixel in np.ndenumerate(frame_np):
                binary = list(format(pixel, "08b"))

                if not count >= len(data):
                    binary[-1] = data[count]
                else:
                    binary[-1] = "0"

                frame_np[index[0], index[1]][index[2]] = int("".join(binary), 2)
                count += 1

            out.write(frame_np)
            print(f"{(frame_number + 1) / total_frames * 100:.2f}%", end="\r")

        video.release()
        out.release()


class Decode:
    def get_LSB_from_image(image_path):
        print_with_empty_line("- Getting Least Significant Bits...")
        image = Image.open(image_path).convert("RGB")
        image_np = np.array(image)
        binary_data = []
        for pixel in np.nditer(image_np):
            binary_data.append(str(pixel % 2))

        return "".join(binary_data)

    def get_LSB_from_video(video_path):
        print_with_empty_line("- Getting Least Significant Bits...")
        video = cv2.VideoCapture(video_path)

    def decode_message(binary_data):
        print_with_empty_line("- Decoding message...")
        buffer = ""
        message = []

        for binary in binary_data:
            buffer += binary
            if len(buffer) >= 8:
                tmp = int("".join(buffer), 2)
                if 31 < tmp < 128:
                    message.append(chr(tmp))
                buffer = ""

        message = "".join(message)
        print_with_empty_line("- Message:\n", message)

    def decode_image(binary_data, file_name):
        print_with_empty_line("- Decoding image...")
        separator = "".join(format(ord(char), "08b") for char in "null")
        binary_data = binary_data.split(separator)
        x = int(len(binary_data[0]) / (3 * 8))
        y = len(binary_data) - 1

        binary_data = list("".join(binary_data))
        binary_data_np = np.array(binary_data)
        pixel_array = []
        rgb = ()

        while binary_data_np.size >= 8:
            rgb += (int("".join(binary_data_np[:8]), 2),)
            binary_data_np = binary_data_np[8:]
            if len(rgb) >= 3:
                pixel_array.append(rgb)
                rgb = ()

        print_with_empty_line("- Creating image...")
        new_image = Image.new("RGB", (x, y))

        image_resolution = x * y
        new_image.putdata(pixel_array[:image_resolution])

        output_path = os.path.join(cwd, "decoded", file_name)
        new_image.save(output_path, "PNG")
        print_with_empty_line("- Image saved as decoded/", file_name)

    def decode_message_from_video(video_path):
        print_with_empty_line("Extracting message...")
        print()

        video = cv2.VideoCapture(video_path)

        if not video.isOpened():
            print("Error opening video file.")
            exit()

        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        msg = []

        for frame_number in range(total_frames):
            ret, frame = video.read()

            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

            frame_np = np.array(frame)

            str_frame_np = (frame_np.ravel() % 2).astype(str)

            while len(str_frame_np) >= 8:
                tmp = int("".join(str_frame_np[:8]), 2)
                str_frame_np = str_frame_np[8:]
                if 31 < tmp < 128:
                    msg.append(chr(tmp))

            print(f"{(frame_number + 1) / total_frames * 100:.2f}%", end="\r")

        msg = "".join(msg)

        video.release()
        print_with_empty_line("Message:\n→", msg)

    def decode_image_from_video(video_path):
        print_with_empty_line("Extracting image...")
        print()

        video = cv2.VideoCapture(video_path)

        if not video.isOpened():
            print("Error opening video file.")
            print()

        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        binary_data = []

        for frame_number in np.arange(total_frames):
            ret, frame = video.read()

            if not ret:
                break

            frame_np = np.array(frame)

            for pixel in np.nditer(frame_np):
                binary_data.append(str(pixel % 2))

            print(f"{(frame_number + 1) / total_frames * 100:.2f}%", end="\r")

        video.release()

        binary_data = "".join(binary_data)
        separator = "".join(format(ord(char), "08b") for char in "null")
        binary_data = binary_data.split(separator)

        x = int(len(binary_data[0]) / (3 * 8))
        y = len(binary_data) - 1

        print()
        print_with_empty_line("- Creating image...")

        new_image = Image.new("RGB", (x, y))

        binary_data = list("".join(binary_data))
        binary_data_np = np.array(binary_data)
        pixel_array = []
        rgb = ()

        while binary_data_np.size >= 8:
            rgb += (int("".join(binary_data_np[:8]), 2),)
            binary_data_np = binary_data_np[8:]
            if len(rgb) >= 3:
                pixel_array.append(rgb)
                rgb = ()

        image_resolution = x * y

        new_image.putdata(pixel_array[:image_resolution])
        new_image_name = "hidden_image_from_video.png"

        output_path = os.path.join(cwd, "decoded", new_image_name)
        new_image.save(output_path, "PNG")
        print_with_empty_line("- Image saved as decoded/", new_image_name)
