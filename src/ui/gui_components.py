import PySimpleGUI as sg

default_font = 'Liberation Sans'


def create_look_and_feel():
    sg.LOOK_AND_FEEL_TABLE['EsmTheme'] = {'BACKGROUND': '#FFFFFF',
                                          'TEXT': '#000000',
                                          'INPUT': '#FFFFFF',
                                          'TEXT_INPUT': '#000000',
                                          'SCROLL': '#4FC3F7',
                                          'BUTTON': ('white', '#4FC3F7'),
                                          'PROGRESS': ('#FFFFFF', '#4FC3F7'),
                                          'BORDER': 0, 'SLIDER_DEPTH': 1, 'PROGRESS_DEPTH': 0,
                                          }


def esm_button(text='', font=(default_font, '18'), key=None, pad=None, size=(None, None)):
    return sg.Button(text,
                     font=font,
                     key=key,
                     enable_events=True,
                     button_color=('white', '#4FC3F7'),
                     size=size,
                     pad=pad,
                     border_width=0,
                     )


def esm_title_text(text='', font=('Arial Bold', '16'), key=None, pad=(300, 1)):
    return sg.Text(text,
                   key=key,
                   font=font,
                   pad=pad,
                   )


def esm_form_text(text='', font=(default_font, '14'), key=None, pad=None, justification='center'):
    return sg.Text(text,
                   key=key,
                   font=font,
                   pad=pad,
                   justification=justification
                   )


def esm_input_text(text='', font=(default_font, '14'), border_width=1, key=None, pad=None, size=(30, 1), enable_events=True):
    return sg.InputText(text,
                        font=font,
                        background_color='white',
                        key=key,
                        pad=pad,
                        size=size,
                        border_width=border_width,
                        enable_events=enable_events
                        )


def esm_input_combo(values=None, font=(default_font, '14'), key=None, pad=None, size=(15, 1), enable_events=True):
    return sg.InputCombo(values=values,
                         font=font,
                         background_color='white',
                         key=key,
                         pad=pad,
                         size=size,
                         enable_events=enable_events
                         )


def esm_listbox(values=None,
                font=(default_font, '14'),
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
              num_rows=15,
              display_row_numbers=False,
              font=(default_font, '14'),
              enable_events=True
              ):
    return sg.Table(values=values,
                    key=key,
                    headings=headings,
                    justification=justification,
                    auto_size_columns=auto_size_columns,
                    num_rows=num_rows,
                    enable_events=enable_events,
                    display_row_numbers=display_row_numbers,
                    font=font,
                    )


def esm_calendar_button(button_text='Calendar',
                        target=(555666777, -1),
                        close_when_date_chosen=True,
                        default_date_m_d_y=(1, 1, 1995),
                        size=(None, None),
                        font=(default_font, '14'),
                        auto_size_button=None,
                        border_width=0,
                        title='Choose date of birth',
                        enable_events=False,
                        key=None,
                        format_calendar="%m/%d/%Y",
                        month_names=None,
                        no_titlebar=True
                        ):
    return sg.CalendarButton(button_text,
                             target=target,
                             title=title,
                             close_when_date_chosen=close_when_date_chosen,
                             default_date_m_d_y=default_date_m_d_y,
                             font=font,
                             border_width=border_width,
                             size=size,
                             auto_size_button=auto_size_button,
                             enable_events=enable_events,
                             key=key,
                             format=format_calendar,
                             month_names=month_names,
                             no_titlebar=no_titlebar
                             )
