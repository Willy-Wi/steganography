from test import Encode, Decode
from PIL import Image
from tkinter import Tk, filedialog
import os


def print_with_empty_line(*args, **kwargs):
    print()
    print(*args, **kwargs)


def main():
    root = Tk()
    root.withdraw()

    cwd = os.getcwd()

    choices = [
        "Encode Message to Image",
        "Encode Image to Image",
        "Encode 2 Images to an Image",
        "Encode Message to Video",
        "Encode Image to Video",
        "Decode Message from Image",
        "Decode Image from Image",
        "Decode 2 Images from an Image",
        "Decode Message from Video",
        "Decode Image from Video",
    ]

    [print(f"{index + 1}. {choice}") for index, choice in enumerate(choices)]

    choice = int(input("→ "))
    host_image = ""

    if not 0 < choice <= len(choices):
        print("That's not a valid input.")
        exit()

    binary_data = ""
    host_image = None

    match choice:
        case 1 | 4:
            message = input("Message: ")
            binary_data = Encode.message_to_binary(message)
        case 2 | 5:
            print_with_empty_line("- Select an Image to embed.")
            image_path = filedialog.askopenfilename()
            binary_data = Encode.image_to_binary(image_path)
        case 3:
            print_with_empty_line("- Select Image(s) to embed.")
            image_path = filedialog.askopenfilenames()

            if (len(image_path)) > 2:
                print("Images is limited to 2.")
                exit()

            seperator = "".join(format(ord(char), "08b") for char in "newimage")
            first_image = Encode.image_to_binary(image_path[0])
            second_image = Encode.image_to_binary(image_path[1])

            binary_data = f"{first_image}{seperator}{second_image}"

    match choice:
        case 1 | 2 | 3 | 6 | 7 | 8:
            print_with_empty_line("- Select host image.")
            image_path = filedialog.askopenfilename()
        case 4 | 5 | 9 | 10:
            print_with_empty_line("- Select host video.")
            video_path = filedialog.askopenfilename()

    match choice:
        case 1 | 2 | 3:
            Encode.encode_to_image(image_path, binary_data)
        case 4 | 5:
            Encode.encode_to_video(video_path, binary_data)

    match choice:
        case 6:
            binary_data = Decode.get_LSB_from_image(image_path)
            Decode.decode_message(binary_data)
        case 7:
            binary_data = Decode.get_LSB_from_image(image_path)
            Decode.decode_image(binary_data, "hidden_image.png")
        case 8:
            binary_data = Decode.get_LSB_from_image(image_path)
            images = binary_data.split("".join(format(ord(char), "08b") for char in "newimage"))
            for index, image in enumerate(images):
                binary_data = image
                Decode.decode_image(binary_data, f"hidden_image_{index + 1}.png")
        case 9:
            Decode.decode_message_from_video(video_path)
        case 10:
            Decode.decode_image_from_video(video_path)


if __name__ == "__main__":
    main()
