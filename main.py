# Normal Imports
import re
import tkinter as tk
import tkinter.scrolledtext as st

# From Imports
from collections import namedtuple
from tkinter import StringVar, Tk, ttk


int_pattern = re.compile(r"^\d+$")
intfloat_pattern = re.compile(r"(^\d+)(\.)?(\d+)?$")


def get_first_int(val, default):
    """Function to see if the supplied val is an integer or starts with an integer, if so return that integer,
otherwise return default.

    Usage:
    >>> get_first_int("250", default=-1)
    250.0
    >>> get_first_int("abc125", default=None)
    None
"""
    match = int_pattern.search(val)
    return int(match.group()) if match is not None else default


def get_int_or_float(val):
    """Function to return `int` or `float` if the given string is one of the two.

    Usage:
    >>> get_int_or_float("123.45")
    123.45
    >>> get_int_or_float("130.0")
    130
    >>> get_int_or_float("130")
    130"""

    match = intfloat_pattern.search(val)
    if match is not None:
        if (match.group(2) is None) or (int(match.group(2)) == 0):
            return int(match.group(0))
        else:
            return float(match.group())
    else:
        return None
        # return int(match.group(0)) if match.group(2) is None else float(match.group())


class DecimalBuilder:
    """Class used to build a number, either an integer or a float."""

    # Possibly use `type` instead of `has_decimal` and store type, ie `int` or `float`; will require validation though.
    __slots__ = ("_value", "_has_decimal")

    def __init__(self, value: str = "", has_decimal: bool = False):
        self._value = value
        self._has_decimal = has_decimal

    @property
    def value(self):
        if not self._value:
            return 0
        return float(self._value) if self._has_decimal else int(self._value)

    def set_val(self, value):
        if type(value) == str:
            val = get_int_or_float(value)
            if val is None:
                if not value:
                    self._value = ""
                    self._has_decimal = False
                return
        else:
            val = value

        val = round(val) if round(val) == val else val

        if type(val) == int:
            self._value = str(val)
            self._has_decimal = False
        elif type(val) == float:
            self._value = str(val)
            self._has_decimal = True

    def get_string_val(self) -> str:
        return self._value

    def clear(self):
        self.set_val("")

    def append(self, value):
        val = str(value)

        if (get_int_or_float(val) is None) and (value != "."):
            raise ValueError("'val' is not of a string or numeric type.")

        if val ==".":
            if self._has_decimal:
                return
            else:
                self._has_decimal = True

        self._value += val


class Calculator(tk.Tk):
    """Class that manages the UI of the Calculator, it inherits from tkinter's Tk()."""

    def __init__(self, title=""):
        """Calculator class initialisor, initialises base class, two display vars of StringVar() type and some other
        class variables that will be used later in the program. Lastly, it calls create_widgets() and update_display()
        to setup the classes widgets and update the output being displayed through the StringVar() class vars."""

        Tk.__init__(self)

        if title:
            self.title(title)

        # Display output vars as StringVar().
        self.current = DecimalBuilder()
        self.display_current = StringVar()
        self.display_history = StringVar()

        # Calculator values.
        self.total = 0
        self.total_prev = 0
        self.history = []

        self.showing_total = False

        # Stores all the widgets for the calculator app.
        self.widgets = {}

        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        """Class method to create all of the widgets required for the current Calculator application. It creates
        widgets for outputting calculation data as well as buttons for inputting data."""

        style = ttk.Style()
        style.configure("od.TButton", background="#0000", borderwidth=0)

        # Main Frame
        self.widgets["main_frame"] = ttk.Frame(self)
        self.widgets["main_frame"].grid(
            row=0, column=0, sticky=(tk.N, tk.E, tk.S, tk.W))

        # Label to display current equation, linked to `self.display_history`.
        self.widgets["output_history_label"] = ttk.Label(self.widgets["main_frame"], justify=tk.RIGHT,
                                                         textvariable=self.display_history)
        self.widgets["output_history_label"].grid(
            row=0, column=0, columnspan=4, sticky=tk.W)

        # Entry to display current value, linked to `self.display_current`.
        self.widgets["output_current_entry"] = ttk.Entry(self.widgets["main_frame"], justify=tk.RIGHT,
                                                         textvariable=self.display_current, state="readonly")
        self.widgets["output_current_entry"].grid(
            row=1, column=0, columnspan=4, sticky=(tk.N, tk.E, tk.S, tk.W))
        # Binding the key and return event handler to handle keyboard key presses.
        self.widgets["output_current_entry"].bind("<Key>", self.key_click)
        self.widgets["output_current_entry"].bind(
            "<Return>", self.return_click())

        # ScrolledText used to output calculation history.
        self.widgets["output_history"] = st.ScrolledText(
            self.widgets["main_frame"], width=23, height=8)
        self.widgets["output_history"].grid(row=0, column=5, rowspan=5)

        # The frame the contains all of the button inputs.
        self.widgets["inputs_frame"] = ttk.Frame(self.widgets["main_frame"])
        self.widgets["inputs_frame"].grid(row=2, column=0, columnspan=4)

        # Create buttons 1 through 9, using a loop and range().
        for button in range(9, 0, -1):
            # Index of current widgets in `self.widgets`.
            current = f"input_button_{str(button)}"

            # Calculate the current row and column using divmod() and then reverse it.
            row, column = divmod(button - 1, 3)
            row = 2 + (2 - row)

            # Add the numeric button input to the grid.
            # Call the button command using lambda to pass value variable.
            self.widgets[current] = ttk.Button(self.widgets["inputs_frame"], text=str(button),
                                               command=lambda val=button: self.number_select(val))
            self.widgets[current].grid(row=row, column=column)
        # Add the `0` numeric button out of the loop.
        self.widgets["input_button_0"] = ttk.Button(self.widgets["inputs_frame"], text="0",
                                                    command=lambda val=0: self.number_select(val))
        self.widgets["input_button_0"].grid(row=5, column=1)

        # Loop through the operators and add them the grid.
        for i, oper in enumerate(('+', '-', '*', "=")[::-1]):
            current = f"input_operator_{oper}"

            # Add the operator button to the grid
            self.widgets[current] = ttk.Button(self.widgets["inputs_frame"], text=str(oper),
                                               command=lambda val=oper: self.operator_select(val))
            self.widgets[current].grid(row=2 + i, column=4)

    def number_select(self, value):
        """Event handling method for handling numeric button clicks, ie buttons 0 through 9."""
        if type(value) is int:
            value = str(value)
        elif type(value) is str:
            val = get_int_or_float(value)
            if val is not None:
                value = val
            else:
                if value == ".":
                    val = "."
                else:
                    return
        else:
            return

        self.showing_total = False

        self.current.append(value)
        self.display_current.set(round(self.current.value, 3))

        # Set focus to the `output_current_entry` widget, for handling keyboard inputs.
        self.widgets["output_current_entry"].focus_set()

    def operator_select(self, operator):
        """Event handling method handling operator button clicks, ie ('+', '-', '*', '/')"""
        if operator in ('+', '-') and self.current.value == 0:
            return
        elif operator in ('*', "/") and self.current.value == 1:
            return

        # Temporarily store total in a local variable
        total = self.total
        self.total_prev = total

        if operator == "=":
            # If the operator is '=', no need to perform calculations.
            self.history.append(self.current.get_string_val())
            self.current.set_val(self.total)
            self.showing_total = True
            self.update_display()
        else:
            # Append the current value and then the operator to the history.
            self.history.append(self.current.get_string_val())
            self.history.append(operator)

            # Update the local `total` to match the operator
            if operator == "+":
                total += self.current.value
            elif operator == "-":
                total -= self.current.value
            elif operator == "*":
                total *= self.current.value
            elif operator == "/'":
                total /= self.current.value

            # Display the current calculation in `output_history` widget.
            self.widgets["output_history"].insert(tk.END, (str(self.total) + " " + operator + " " + self.current.get_string_val() +
                                                           " = " + str(total)) + "\n")
            self.current.clear()
            self.showing_total = True
            self.update_display(total)
        self.total = total

        # Set focus to the `output_current_entry` widget, for handling keyboard inputs.
        self.widgets["output_current_entry"].focus_set()

    def return_click(self):
        """Handle the enter key click"""
        # Does seem to be calling at the moment, will need to take a look at it.
        self.operator_select("=")

    def key_click(self, event):
        """Handle a keyboard key click, perform operation if it is of a valid  value, ie number or operator."""
        val = get_first_int(event.char, None)
        if val is not None:
            # If the entered key is a number, then call `self.number_select()` with the inputted number.
            self.number_select(val)
        else:
            # If the entered key is an operator, then call `self.operator_select()` with the inputted operator.
            if event.char == ".":
                self.number_select(event.char)
            elif event.char in ("+", "-", "*", "/", "="):
                self.operator_select(event.char)

    def update_display(self, new_total=0):
        """Method to  update the data being displayed to the user by setting `self.display_current` and
        `self.display_history` StringVar() which are linked to widgets defined in `create_widgets()`."""
        self.display_current.set(
            new_total if self.showing_total else self.current.get_string_val())
        self.display_history.set(self.get_history_output())

    def get_history_output(self):
        """Create a string using the last operator and number from `self.history` and `self.total_prev`."""
        out = ""

        if len(self.history) >= 2:
            out += " "
            out += self.history[-1]
            out += " "
            out += self.history[-2]

        return str(self.total_prev) + out


if __name__ == "__main__":
    # Create an instance of the Calculator class and begin its `mainloop()`.
    app = Calculator(title="Simple Calculator")
    app.mainloop()
