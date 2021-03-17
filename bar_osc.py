"""
Bar Osc App

Calibration oscillator for the macOS menu bar
"""

import math
import rumps
from oscillator import Oscillator

rumps.debug_mode(True)

APP_ICON = 'barosc_logo.png'

# ------------------------------ Helper Functions ------------------------------

def slider_to_freq(value):
    """
    convert slider value to frequency (20Hz-20kHz)

    base-2 logarithmic slider
    """
    return round(math.pow(2, value * 1e-4))

def freq_to_slider(freq):
    """
    convert frequency (20Hz-20kHz) to slider value

    base-2 logarithmic slider
    """
    return math.log2(freq) * 1e4

def freq_title_format(freq):
    """
    e.g. Frequency: 440 Hz
    e.g. Frequency: 15.0 kHz
    """
    if freq < 10000:
        title = f"Frequency: {round(freq, 1)} Hz"
    elif freq >= 10000:
        freq = round(freq * 1e-3, 1)
        title = f"Frequency: {freq} kHz"
    return title

def amp_title_format(amp):
    """
    e.g. Volume: -0.0 dBFS
    e.g. Volume: -∞ dBFS
    """
    try:
        dbfs = round(20 * math.log10(amp), 1)
    except ValueError:
        dbfs = "-∞"
    if dbfs == 0.0:
        dbfs = "-0.0"
    return f"Volume: {dbfs} dBFS"

# -------------------------------- Menu Bar App --------------------------------

class BarOscApp:
    """ Bar Osc object """

    def __init__(self):
        # initial oscillator settings
        self.samplerate = 44100
        self.wave_type = "sine_wave"
        self.amplitude = 0.5
        self.frequency = 440
        self.store_wave = None
        self.store_freq = None

        # config
        app_title = "Bar Osc"
        interval = 2                        # seconds per calibration step

        # object instances
        self.app = rumps.App(app_title, icon=APP_ICON)
        self.oct_timer = rumps.Timer(self.advance_octave, interval)
        self.oct_thirds_timer = rumps.Timer(self.advance_octave_thirds, interval)
        self.osc = Oscillator(  self.samplerate,
                                self.wave_type,
                                self.amplitude,
                                self.frequency)
        # set up menu
        self.build_menu()
        self.osc_ready_menu()


    def build_menu(self):
        """ define menu, buttons, sliders """
        # menu items
        self.start_button = rumps.MenuItem(                 # Start Osc
            title="Start Oscillator")
        self.stop_button = rumps.MenuItem(                  # Stop Osc
            title="Stop Oscillator")
        self.amp_title = rumps.MenuItem(                    # Volume title
            title=amp_title_format(self.amplitude),
            callback=None)
        self.amp_slider = rumps.SliderMenuItem(             # Volume slider
            value=self.amplitude,
            min_value=0.0,
            max_value=1.0,
            callback=self.adj_amp,
            dimensions=(200, 20))
        self.sine_wave_button = rumps.MenuItem(             # Sine Wave
            title="Sine Wave",
            callback=None)
        self.square_wave_button = rumps.MenuItem(           # Square Wave
            title="Square Wave",
            callback=self.set_square_wave)
        self.white_noise_button = rumps.MenuItem(           # White Noise
            title="White Noise",
            callback=self.set_white_noise)
        self.pink_noise_button = rumps.MenuItem(            # Pink Noise
            title="Pink Noise",
            callback=self.set_pink_noise)
        self.freq_title = rumps.MenuItem(                   # Frequency: title
            title=freq_title_format(self.frequency),
            callback=None)
        self.freq_slider = rumps.SliderMenuItem(            # Frequency slider
            value=freq_to_slider(self.frequency),
            min_value=freq_to_slider(20),                   # 20Hz - 20kHz
            max_value=freq_to_slider(20000),
            callback=self.adj_freq,
            dimensions=(200, 20))
        self.octave_button = rumps.MenuItem(                # Octave Walk
            title="Octave Walk",
            callback=self.begin_octave_walk)
        self.octave_thirds_button = rumps.MenuItem(         # Octave Walk 1/3
            title="Octave Walk  ⅓",
            callback=self.begin_octave_walk_thirds)
        #populate menu
        self.app.menu =    [self.start_button,
                            self.stop_button,
                            None,
                            self.amp_title,
                            self.amp_slider,
                            None,
                            self.sine_wave_button,
                            self.square_wave_button,
                            self.white_noise_button,
                            self.pink_noise_button,
                            None,
                            self.freq_title,
                            self.freq_slider,
                            None,
                            self.octave_button,
                            self.octave_thirds_button,
                            None]


# ------------------------ Menu Bar App: Menu UI Methods -----------------------

    def osc_ready_menu(self):
        """ menu while not playing osc """
        #self.app.title = "🎛"
        self.start_button.set_callback(self.start_osc)
        self.stop_button.set_callback(None)

    def osc_busy_menu(self):
        """ menu while playing osc """
        #self.app.title = "🔊"
        self.start_button.set_callback(None)
        self.stop_button.set_callback(self.stop_osc)

    def wave_change_menu(self, old_wave_type, new_wave_type):
        """ menu change when selecting new wave type """
        try:
            eval("self." + new_wave_type + "_button.set_callback(None)")
            eval("self." + old_wave_type + "_button.set_callback(self.set_" + old_wave_type + ")")
        except NameError as wave_error:
            raise NotImplementedError("Wave Type (methods) not available") from wave_error


# --------------------------- Menu Bar App: Callbacks --------------------------

    def start_osc(self, sender):
        """ Start Oscillator callback """
        self.osc_busy_menu()
        self.osc.play()

    def stop_osc(self, sender):
        """ Stop Oscillator callback """
        self.osc_ready_menu()
        self.osc.stop()

    def set_sine_wave(self, sender):
        """ Sine Wave callback """
        self.wave_change_menu(self.osc.wave_type, 'sine_wave')
        self.osc.wave_type = 'sine_wave'

    def set_square_wave(self, sender):
        self.wave_change_menu(self.osc.wave_type, 'square_wave')
        self.osc.wave_type = 'square_wave'

    def set_white_noise(self, sender):
        """ White Noise callback """
        self.wave_change_menu(self.osc.wave_type, 'white_noise')
        self.osc.wave_type = 'white_noise'

    def set_pink_noise(self, sender):
        """ Pink Noise callback """
        self.wave_change_menu(self.osc.wave_type, 'pink_noise')
        self.osc.wave_type = 'pink_noise'

    def advance_octave(self, sender):
        """
        Timer callback
        """
        if self.osc.stream:
            self.stop_osc(sender=None)
        self.osc.frequency *= 2
        if self.osc.frequency > 1760:
            self.oct_timer.stop()
            # return to original settings
            self.osc.wave_type = self.store_wave
            self.osc.frequency = self.store_freq
        else:
            rumps.notification( title='Octave Walk',
                                subtitle=None,
                                message=freq_title_format(self.osc.frequency),
                                sound=False,
                                icon=APP_ICON)

            self.osc.play()

    def advance_octave_thirds(self, sender):
        """
        Timer callback
        """
        if self.osc.stream:
            self.stop_osc(sender=None)
        self.osc.frequency *= 2**(1/3)
        if self.osc.frequency > 1760:
            self.oct_thirds_timer.stop()
            # return to original settings
            self.osc.wave_type = self.store_wave
            self.osc.frequency = self.store_freq
        else:
            rumps.notification( title='Octave Walk  ⅓',
                                subtitle=None,
                                message=freq_title_format(self.osc.frequency),
                                sound=False,
                                icon=APP_ICON)

            self.osc.play()

    def begin_octave_walk(self, sender):
        """
        Octave Walk callback
        Walk up by octave: A0 (27.5 Hz) - A6 (1760 Hz)
        """
        # stop osc if playing
        if self.osc.stream:
            self.stop_osc(sender=None)
        # remember settings
        self.store_wave = self.osc.wave_type
        self.store_freq = self.osc.frequency
        # initial calibration settings
        self.osc.wave_type = 'sine_wave'
        self.osc.frequency = 27.5
        # begin
        self.oct_timer.start()

    def begin_octave_walk_thirds(self, sender):
        """
        Octave Walk 1/3 callback
        Walk up by 1/3 octave: A0 (27.5 Hz) - A6 (1760 Hz)
        """
        # stop osc if playing
        if not self.osc.stream is None:
            self.stop_osc(sender=None)
        # remember settings
        self.store_wave = self.osc.wave_type
        self.store_freq = self.osc.frequency
        # initial calibration settings
        self.osc.wave_type = 'sine_wave'
        self.osc.frequency = 27.5
        # begin
        self.oct_thirds_timer.start()

    def adj_freq(self, sender):
        """ Frequency slider callback """
        frequency = slider_to_freq(self.freq_slider.value)
        self.freq_title.title = freq_title_format(frequency)    # update title
        self.osc.frequency = frequency                          # update oscillator
        print(f'SLIDER ===> {self.freq_slider.value}, FREQ ===> {self.osc.frequency}')

    def adj_amp(self, sender):
        """ Amplitude slider callback """
        self.amp_title.title = amp_title_format(self.amp_slider.value)# update title
        self.osc.amplitude = self.amp_slider.value                    # update oscillator
        print(f'SLIDER ===> {self.amp_slider.value}, AMP ===> {self.osc.amplitude}')

    def run(self):
        """ run it """
        self.app.run()


# ---------------------------------- Run Time ----------------------------------

if __name__ == '__main__':
    app = BarOscApp()
    app.run()
