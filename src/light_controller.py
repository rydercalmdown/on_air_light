import os
import time
import board
import neopixel
import logging


class LightController():
    """Class for controlling LEDs"""

    def __init__(self):
        """Instantiate the module"""
        self._set_defaults()
        self._setup_neopixels()

    def _set_defaults(self):
        """Setup the defaults"""
        self.pin = board.D18 
        self.count = 16
        self.brightness = 1

    def _setup_neopixels(self):
        self.pixels = neopixel.NeoPixel(
            self.pin,
            self.count,
            brightness=self.brightness,
            auto_write=False,
            pixel_order=neopixel.RGB
        )

    def flash_leds(self, num_times=10, delay=0.3):
        """Flashes all the LEDs"""
        logging.info('Flashing LEDs')
        for _ in range(0, num_times):
            self.pixels.fill((255, 255, 255))
            self.pixels.show()
            time.sleep(delay)
            self.pixels.fill((0, 0, 0))
            self.pixels.show()
            time.sleep(delay)

    def test(self):
        """Tests the lights"""
        self.flash_leds()
    
    def turn_leds_on(self):
        """Turns the LEDs on"""
        self.flash_leds()
        logging.info('Turning LEDs On')
        self.pixels.fill((255, 255, 255))
        self.pixels.show()
    
    def turn_leds_off(self):
        """Turns the LEDs off"""
        logging.info('Turning LEDs Off')
        self.pixels.fill((0, 0, 0))
        self.pixels.show()


if __name__ == "__main__":
    lc = LightController()
    lc.test()
