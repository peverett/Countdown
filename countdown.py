"""
Simple countdown timer

Countdown is in minutes and seconds and digits are displayed in green. 
They change to Amber with < 30 seconds and red when < 10.

* The window frame is always on top and borderless
* 2-minutes by default.
* It can be placed in the corner of any monitor. 
* Windows OS only
"""

__version__ = "2.1"
__author__ = "simon.peverett@gmail.com"
__all__ = ['__version__', '__author__']

import sys
if sys.version_info < (3, 7):
    raise SystemExit("Python 3.7 or better required.")
elif sys.platform != "win32":
    raise SystemExit("Only Windows OS platfrom supported.")
try:
    import win32api
except ModuleNotFoundError:
    raise SystemExit(
        "The 'win32api' library is not installed."
        "To install it use, please use the command...\n"
        "\tpython -m pip install pywin32"
        )
import winsound                 # Window's platform only.
import argparse
import os
from tkinter import *
from tkinter import messagebox
from tkinter.font import Font

# Play the WAV file named countdown_alarm.wav in the same directory as this
# script.
ALARM_WAV = os.path.join( 
        os.path.dirname(os.path.realpath(__file__)), 
        "countdown_alarm.wav"
        )

def parse_args(argv):
    """Parse command line arguments and set defaults
    * Monitor 1 by default
    * Top left corner by default
    * 2-minutes timer by default
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--display", type=int, nargs="?", default=1,
        help="The screen/monitor to display on, the default is 1.",
        )
    parser.add_argument(
        "-m", "--minutes", type=int, nargs="?", default=2,
        help="Count down minutes, range is 0..99, default is 2."
        )
    parser.add_argument(
        "-s", "--seconds", type=int, nargs="?", default=0,
        help="Count down seconds, range is 0..59, default is 0."
        )
    parser.add_argument(
        "-p", "--position", type=str, nargs="?", default="br",
        help="Position on screen for the timer, options are: "
        "tl (top left), tr (top right), bl (bottom left), "
        "br (bottom right - default)"
        )
    return parser.parse_args(argv)

class CountdownTimer():
    """The Countdown Timer
    * Implemented as a Tkinker frame, without border and always on top.
    * Manages the positioning of the frame in the display corners.
    * Manages the monitor on which it is displayed.

    The actual frame has a display for minutes and seconds.
    An 'x' button in the top left to close the app.
    A start/Stop button that is modal
    A reset button.
    """

    def __init__(self, root, args):
        """Initialise the Countdown Timer, with args from the command line."""
        self.root = root
        self.args = args

        # Tell the window manager this is a splash window, so no border and no
        # title bar.
        self.root.wm_overrideredirect(True)

        self.c18 = Font(family="Consolas", size=16)
        self.c36 = Font(family="Consolas", size=36)
        self.timer = StringVar()
        self.after_id = None
        self.ssStr = StringVar()
        self.ssStr.set("Start")
        self.minutes = self.config_mins = args.minutes
        self.seconds = self.config_secs = args.seconds
        self.timer.set("{:02}:{:02}".format(self.minutes, self.seconds))
        self.flash = True

        self.initCountdownFrame()

        # Refresh and set the CountdownTimer frame on-top
        self.root.update_idletasks()
        self.root.attributes("-topmost", "true")

        self.initPositionManagement()
        #self.position(self.args.position.lower())

    def initCountdownFrame(self):
        """Create the Frame for the Countdown app, buttons, etc."""
        self.frm = Frame(self.root, bd=1, height=300, width=200, bg="black" )
        self.frm.pack(side=TOP, fill=X, expand=NO)

        self.quit = Button( 
                self.frm, text="X", fg="Red", bg="black", width=3, 
                command=self.destroy, 
                font=Font(family="Consolas", size=12, weight="bold")
                )
        self.quit.pack(side=TOP, anchor=E)

        self.legend = Label(
                self.frm, textvariable=self.timer, width=7, justify=CENTER,
                padx=5, pady=5, bg="black", fg="green2", font=self.c36
                )
        self.legend.pack(side=TOP, fill=X, expand=YES)

        self.btnf = Frame( self.frm, bd=5, bg="black")

        self.btnf.pack(side=BOTTOM, fill=X, expand=YES)
        self.strtstp = Button(
                self.btnf, textvariable=self.ssStr, fg="black", bg="green2", 
                padx=3, pady=3, font=self.c18, width=6, command=self.startStop
                )
        self.strtstp.pack(side=LEFT, anchor=W, fill=X, expand=YES)

        self.reset = Button(
                self.btnf, text="Reset", fg="white", bg="blue",
                padx=3, pady=3, font=self.c18, width=6, command=self.Reset
                )
        self.reset.pack(side=LEFT, anchor=E, fill=X, expand=YES)

        self.pf = Frame( self.frm, bd=20, bg="black")
        self.pf.pack(side=TOP, fill=X, expand=YES)

    def destroy(self):
        """Destroy the window and exit TK when 'x' button is clicked."""
        self.root.destroy()

    def startStop(self):
        """Handle the Start/Stop button event"""
        if self.ssStr.get() == "Start":
            self.ssStr.set("Stop")
            self.strtstp.configure(bg="red", fg="white")
            self.after_id=self.frm.after(1000, self.decTimer)
        else:
            self.ssStr.set("Start")
            self.strtstp.configure(bg="green2",fg="black")
            self.frm.after_cancel(self.after_id)
            self.after_id = None

    def Reset(self):
        """Handle the Reset button event"""
        if self.after_id:
            self.frm.after_cancel(self.after_id)
            self.after_id = None
        if self.ssStr.get() == "Stop":
            self.ssStr.set("Start")
            self.strtstp.configure(bg="green2", fg="black")
            self.strtstp.configure(state=NORMAL)
        self.minutes=self.config_mins
        self.seconds=self.config_secs
        self.legend.configure(fg="green2")
        self.Flash = True
        self.timer.set("{:02}:{:02}".format(self.minutes, self.seconds))

    def decTimer(self):
        """Decrement the timer by one second and update th display"""
        # TODO: okay for short timer, how accurate is this for longer though?
        if self.seconds == 0:
            if self.minutes:
                self.minutes -= 1
                self.seconds = 59
        else:
            self.seconds -= 1
            if self.minutes < 1:
                if self.seconds == 30:
                    self.legend.configure(fg="gold")
                elif self.seconds == 10:
                    self.legend.configure(fg="red")

        self.timer.set("{:02}:{:02}".format(self.minutes, self.seconds))

        if self.seconds <= 0 and self.minutes <= 0:
            self.strtstp.configure(state=DISABLED)
            if os.path.exists(ALARM_WAV):
                winsound.PlaySound(
                        ALARM_WAV,
                        winsound.SND_FILENAME | winsound.SND_ASYNC
                        )
            self.after_id = self.frm.after(500, self.FlashRed)
        else:
            self.after_id = self.frm.after(1000, self.decTimer)

    def FlashRed(self):
        """Flash the digits when the timer expired"""
        if self.flash:
            self.legend.configure(fg="black")
        else:
            self.legend.configure(fg="red")
        self.flash =  not self.flash
        self.after_id = self.frm.after(500, self.FlashRed)

    ###
    # Position management functions, for locating the window in the correct
    # corner on the correct display.

    # Indexes into the 'work_area' tuple
    TL_X = 0 # Top Left X of work area on monitor 
    TL_Y = 1 # Top Left Y
    BR_X = 2 # Bottom Right X
    BR_Y = 3 # Bottom Right Y

    def initPositionManagement(self):
        """Get the monitors whandle, and count how many there are. 
        This allows the app to validate the monitor selected to display on.
        Then get the 'work area' of the selected monitor, to be used
        for calculating the countdown frames position on that monitor."""
        self.monitors = win32api.EnumDisplayMonitors()
        # self.monitors = 
        #     [(<PyHANDLE:7144979>, <PyHANDLE:0>, (0, 0, 1920, 1080)),
        #      (<PyHANDLE:52694571>, <PyHANDLE:0>, (1920, 0, 3840, 1080))]
        self.no_of_monitors = len(self.monitors)

        if self.args.display < 1 or self.args.display > self.no_of_monitors:
            raise SystemExit(
                "The command line arguement 'display' is {} outside the allowed"
                " the allowed range 1..{}".format(self.args.display, self.no_of_monitors)
                )
        monitor_pyhandle = self.monitors[self.args.display-1][0]
        monitor_info = win32api.GetMonitorInfo(monitor_pyhandle)
        # monitor_info = 
        #     {'Monitor': (0, 0, 1920, 1080),
        #      'Work': (0, 0, 1920, 1040),
        #      'Flags': 1,
        #      'Device': '\\\\.\\DISPLAY1'}
        self.work_area = monitor_info['Work']

        self.pos_dispatcher = {
                'tl':   self.TopLeft,
                'tr':   self.TopRight,
                'bl':   self.BottomLeft,
                'br':   self.BottomRight
                }
        
        position_func = self.pos_dispatcher.get(self.args.position.lower())
        if position_func:
            position_func()
        else:
            raise SystemExit(
                "The comamnd line argument 'position' is outside the allowed"
                " range 'tl', 'tr', 'bl' or 'br'." 
                )


    def TopLeft(self):
        """Position the 'toplevel' window so it is in the top left corner of
        the work_area
        The work_area tuple is (top x, top y, bottom x, bottom y"""
        self.root.geometry("+{}+{}".format(
            self.work_area[self.TL_X], 
            self.work_area[self.TL_Y])
            )

    def GetRootGeometry(self):
        """Get the geometry of the root window, which is in the format
        root.geometry()='198x162+0+0'. Convert that string to return the
        first two integer elements of the string that are the width (x) and 
        height (y)"""
        return tuple( 
            int(_) for _ in self.root.geometry().split('+')[0].split('x')
            )

    def BottomRight(self ):
        """Position the root window so it is in the bottom right corner of
        the work area, This is done by taking the bottom right coord and 
        subtracting the root window size.
        """
        width, height = self.GetRootGeometry()
        x = self.work_area[self.BR_X] - width
        y = self.work_area[self.BR_Y] - height
        self.root.geometry("+{}+{}".format(x, y))

    def TopRight(self):
        """Position the window so it is top right"""
        width, _ = self.GetRootGeometry()
        x = self.work_area[self.BR_X] - width
        self.root.geometry("+{}+{}".format(x, self.work_area[self.TL_Y]))

    def BottomLeft(self):
        """Position the window so it is bottom left"""
        _, height = self.GetRootGeometry()
        y = self.work_area[self.BR_Y] - height
        self.root.geometry("+{}+{}".format(self.work_area[self.TL_X], y))

def main():
    """Main function"""
    args = parse_args(sys.argv[1:])
    
    if args.minutes < 0 or args.minutes > 99:
        raise SystemExit(
            "The comamnd line argument 'minutes' is outside the allowed"
            " range 0..99."
            )
    elif args.seconds < 0 or args.seconds > 59:
        raise SystemExit(
            "The comamnd line argument 'seconds' is outside the allowed"
            " range 0..59."
            )
    elif args.position not in ['tl', 'tr', 'bl', 'br']:
        raise SystemExit(
            "The command line argument 'position' must be one of: "
            "'tl', 'tr', 'bl' or 'br'"
            )

    root = Tk()
    control = CountdownTimer(root, args)
    root.mainloop()
    
if __name__ == "__main__":
    main()
