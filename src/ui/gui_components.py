import PySimpleGUI as sg


def create_look_and_feel():
    sg.LOOK_AND_FEEL_TABLE['EsmTheme'] = {'BACKGROUND': '#FFFFFF',
                                          'TEXT': '#000000',
                                          'INPUT': '#FFFFFF',
                                          'TEXT_INPUT': '#000000',
                                          'SCROLL': '#4FC3F7',
                                          'BUTTON': ('white', '#4FC3F7'),
                                          'PROGRESS': ('#FFFFFF', '#4FC3F7'),
                                          'BORDER': 1, 'SLIDER_DEPTH': 1, 'PROGRESS_DEPTH': 0,
                                          }


def esm_button(text='', font='Yukarimobile 25', key=None, pad=None, size=(None, None)):
    button = sg.Button(text,
                       font=font,
                       key=key,
                       enable_events=True,
                       button_color=('white', '#4FC3F7'),
                       size=size,
                       pad=pad,
                       border_width=0,
                       )

    return button


def esm_title_text(text='', font='Yukarimobile 18', key=None, pad=(300, 1)):
    title_text = sg.Text(text,
                         key=key,
                         font=font,
                         pad=pad,
                         )

    return title_text


def esm_form_text(text='', font='Helvetica 14', key=None, pad=None):
    form_text = sg.Text(text,
                        key=key,
                        font=font,
                        pad=pad,
                        )

    return form_text


def esm_input_text(text='', font='Helvetica 14', key=None, pad=None, size=(35, 1)):
    input_text = sg.InputText(text,
                              font=font,
                              background_color='white',
                              key=key,
                              pad=pad,
                              size=size,
                              )

    return input_text


def esm_input_combo(values=None, font='Helvetica 14', key=None, pad=None, size=(25, 1)):
    input_combo = sg.InputCombo(values=values,
                                font=font,
                                background_color='white',
                                key=key,
                                pad=pad,
                                size=size,
                                )

    return input_combo


def esm_listbox(values=None, font='Helvetica 14', key=None, pad=None, size=(25, 10), enable_events=False):
    listbox = sg.Listbox(values=values,
                         background_color='white',
                         enable_events=enable_events,
                         font=font,
                         key=key,
                         pad=pad,
                         size=size
                         )

    return listbox
