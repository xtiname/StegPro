import os
from PIL import Image
import PySimpleGUI as sg
import webbrowser


max_color_value = 255
max_bit_value = 8


def remove_least_significant_bit(value):
    value = value >> 1
    return value << 1


def get_least_significant_bit(value):
    value = value << max_bit_value - 1
    value = value % max_color_value
    return value >> max_bit_value - 1


def get_most_significant_bit(value):
    return value >> max_bit_value - 1


def shift_bit(value):
    return value << max_bit_value - 1


def make_image(data, resolution):
    image = Image.new("RGB", resolution)
    image.putdata(data)
    return image


def encode(image_to_hide, image_to_hide_in):
    width, height = image_to_hide_in.size

    hide_image = image_to_hide.load()
    hide_in_image = image_to_hide_in.load()

    data = []

    for y in range(height):
        for x in range(width):
            r_hide, g_hide, b_hide = hide_image[x, y]

            r_hide = get_most_significant_bit(r_hide)
            g_hide = get_most_significant_bit(g_hide)
            b_hide = get_most_significant_bit(b_hide)

            r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]

            r_hide_in = remove_least_significant_bit(r_hide_in)
            g_hide_in = remove_least_significant_bit(g_hide_in)
            b_hide_in = remove_least_significant_bit(b_hide_in)

            data.append((r_hide + r_hide_in,
                         g_hide + g_hide_in,
                         b_hide + b_hide_in))

    return make_image(data, image_to_hide.size)


def decode(image_to_decode):
    width, height = image_to_decode.size
    encoded_image = image_to_decode.load()

    data = []

    for y in range(height):
        for x in range(width):
            r_encoded, g_encoded, b_encoded = encoded_image[x, y]

            r_encoded = get_least_significant_bit(r_encoded)
            g_encoded = get_least_significant_bit(g_encoded)
            b_encoded = get_least_significant_bit(b_encoded)

            r_encoded = shift_bit(r_encoded)
            g_encoded = shift_bit(g_encoded)
            b_encoded = shift_bit(b_encoded)

            data.append((r_encoded, g_encoded, b_encoded))

    return make_image(data, image_to_decode.size)


sg.theme('Light Blue 2')

file_types = [("JPEG (*.jpg)", "*.jpg"),
              ("PNG (*.png)", "*.png"),
              ("All files (*.*)", "*.*")]
png_type = [("PNG (*.png)", "*.png")]

menu_def = [['Help', ['About App']]]
url = 'https://github.com/xtiname/StegPro/blob/main/README.md'


def main():
    layout = [
              [sg.Menu(menu_def, size=(200,200))],
              [sg.Text('Welcome to StegPro!', font=("Courier New", 20))],
              [sg.Text('', font=("Courier New", 15))],
              [sg.Text('What would you like to do?', font=("Courier New", 15))],
              [sg.Text('', font=("Courier New", 15))],
              [sg.Text('', font=("Courier New", 15))],
              [sg.Button('Encode Image', font=("Courier New", 15))],
              [sg.Button('Decode Image', font=("Courier New", 15))],
              [sg.Text('', font=("Courier New", 70))],
              [sg.Text('Krystsina Rytsikava - 2022 - Mendel University in Brno', text_color='white smoke')],
              ]

    window = sg.Window('StegPro', layout, size=(520, 400), element_justification='c')

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            break

        if event == 'Encode Image':
            layout = [
                [sg.Text('Cover Image'), sg.Input(key='file1'), sg.FileBrowse(file_types=file_types)],
                [sg.Text('Secret Image'), sg.Input(key='file2'), sg.FileBrowse(file_types=file_types)],
                [sg.Output(size=(68, 18), key='output'), [sg.Image(key='-ENCODED-IMAGE-')]],
                [sg.Submit(), sg.Input(key='Save', visible=False, enable_events=True),
                 sg.FileSaveAs(file_types=png_type),
                 sg.Cancel()],
            ]

            window = sg.Window('StegPro', layout, size=(520, 440))

            while True:
                event, values = window.read()
                if event in (None, 'Cancel'):
                    break
                elif event == 'Submit':
                    image_to_hide_in = values['file1']
                    image_to_hide = values['file2']
                    if os.path.exists(image_to_hide_in and image_to_hide):
                        image_to_hide_in = Image.open(image_to_hide_in)
                        image_to_hide = Image.open(image_to_hide)
                        if image_to_hide.size < image_to_hide_in.size:
                            image_to_hide = image_to_hide.resize(image_to_hide_in.size)

                            encoded_image = encode(image_to_hide, image_to_hide_in)
                            print('Image is successfully encoded. Click "Save As..." button to save it.')

                        elif image_to_hide.size > image_to_hide_in.size:
                            print('Cover Image size is smaller than Secret Image size. Please try again!')

                elif event == 'Save':
                    encoded_image.save(values['Save'])

            window.close()

        if event == 'Decode Image':
            layout = [
                [sg.Image(key='-DECODED-IMAGE-')],
                [sg.Text('Image to decode'), sg.Input(key='file1'), sg.FileBrowse(file_types=png_type)],
                [sg.Output(size=(68, 20), key='output')],
                [sg.Submit(), sg.Input(key='Save', visible=False, enable_events=True),
                 sg.FileSaveAs(file_types=file_types),
                 sg.Cancel()],
            ]

            window = sg.Window('StegPro', layout, size=(520, 440))

            while True:
                event, values = window.read()
                if event in (None, 'Exit', 'Cancel'):
                    break
                elif event == 'Submit':
                    image_to_decode = values['file1']
                    if os.path.exists(image_to_decode):
                        image_to_decode = Image.open(image_to_decode)
                        decoded_image = decode(image_to_decode)
                        print('Image is successfully decoded. Click "Save As..." button to save it.')

                elif event == 'Save':
                    decoded_image.save(values['Save'])

            window.close()

        if event == 'About App':
            webbrowser.open(url)

    window.close()

    
if __name__ == '__main__':
    main()
