__author__ = 'joaci'

import subprocess, time

print 'intanciating driver..'

time.sleep(1)

print 'switching auto-exposure off..'
subprocess.call(["v4l2-ctl", "-c", "auto_exposure=1"])
print 'switching white_balance to manual..'
subprocess.call(["v4l2-ctl", "-c", "white_balance_auto_preset=0"])
print 'disabling power_line_frequency detection..'
subprocess.call(["v4l2-ctl", "-c", "power_line_frequency=0"])
print 'decreasing saturation set point (ideally it should be fixed but..)'
subprocess.call(["v4l2-ctl", "-c", "saturation=-30"])
