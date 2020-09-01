import PySimpleGUI as sg


FONT = 'Noto Sans'


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


def esm_button(text='', font=(FONT, '25'), key=None, pad=None, size=(None, None)):
    return sg.Button(text,
                     font=font,
                     key=key,
                     enable_events=True,
                     button_color=('white', '#4FC3F7'),
                     size=size,
                     pad=pad,
                     border_width=0,
                     )


def esm_title_text(text='', font=(FONT, '14'), key=None, pad=(300, 1)):
    return sg.Text(text,
                   key=key,
                   font=font,
                   pad=pad,
                   )


def esm_form_text(text='', font=(FONT, '14'), key=None, pad=None, justification='center'):
    return sg.Text(text,
                   key=key,
                   font=font,
                   pad=pad,
                   justification=justification
                   )


def esm_input_text(text='', font=(FONT, '14'), key=None, pad=None, size=(35, 1)):
    return sg.InputText(text,
                        font=font,
                        background_color='white',
                        key=key,
                        pad=pad,
                        size=size,
                        )


def esm_input_combo(values=None, font=(FONT, '14'), key=None, pad=None, size=(25, 1)):
    return sg.InputCombo(values=values,
                         font=font,
                         background_color='white',
                         key=key,
                         pad=pad,
                         size=size,
                         )


def esm_listbox(values=None,
                font=(FONT, '14'),
                default_values=[],
                select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                key=None,
                pad=None,
                size=(30, 10),
                enable_events=False
                ):
    return sg.Listbox(values=values,
                      default_values=default_values,
                      background_color='white',
                      enable_events=enable_events,
                      select_mode=select_mode,
                      font=font,
                      key=key,
                      pad=pad,
                      size=size
                      )


def esm_table(values,
              key=None,
              headings=None,
              auto_size_columns=True,
              justification='left',
              num_rows=20,
              font=(FONT, '13'),
              enable_events=True
              ):
    return sg.Table(values=values,
                    key=key,
                    headings=headings,
                    justification=justification,
                    auto_size_columns=auto_size_columns,
                    num_rows=num_rows,
                    enable_events=enable_events,
                    font=font)
