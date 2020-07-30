from kivy.gesture import GestureDatabase
from kivy.uix.boxlayout import BoxLayout
from kivy.gesture import Gesture

gesture_strings = {
    'left_to_right_line': 'eNq1mE1y3DYQhfe8iLXRFPofuICyTZUOkFLsKVllR5qSxkl8+zS7ZWWaFYfYaDajeQQf8PUDAVBXD18e/vx+uD++nL89H5dfXr9Pbbn6dILl9sPj3R/HD8sJ/U//ouXl9sPL+fnpy/HFf/Jy9fUky9V/mtxGs+Wkq5X5/aenh8fzeltfbxs/ue3XtdVyghzBOoTvfgvgctMOrQFpgz6odeEm1Nfx/L1ep+Xmuh2MGzJAM8HBXWV5+f3u/7vh6EaW+5/3cP/DvHU1Q0W2gebtd80DHSzNr+3AQm0gNGC3aXS8bvKvvWqXJm1oEzBk3bfvYT8m7QmVrI1GgJ3Jdu0xEkCYtG/aAQEVeus89iuPGPY0Zy8ioAjDBmjX1vftI1iUOXseStTfEoCJ6kS2aO/mH+HiZLiso1kfnYFJWPftKcKlyXAZGoqwsBFYh0H7/pEu0bv5R7w0GS+JzxkRVC+NDb931z7SJXsv+wiXJsMlAJRh0vvwpaftLwwc4fJkuL4aNP/YayPYLz5HuDwZLjLSIOjWjTxb3F8aOMLlyXCxIfo1BGZFvz4x/kiX7d38I16ejNcfWRrGAxuxNBu79hLxCryXfaQrk+m+7bU4RFHH/tIjka5Mpuvbiu+2zafoMCXfBfb9I12ZTNc3WzHxChHjMLS+//RKxCuT8b5NHEH0rdcmFjeNgHUmYPf3w8IAMFITtS77y4NGwEpz9uzLjwJZb6aGfT9fjXxV5uxNwfXmxy1jJtzf2DXiVZuyh8a9DViH7se53vZnj0a4OubsyY9UPvFxLcx6wNq1t4jW5qIFVWnYzISHL6Iz9hGtzUULozeVgb65+PFkYuJbJGtzySIOXxO88MqjC1lMnPXt4ePz8fj49i5gur4M+NWrG6ZDW24Yzb/OJ+vLnWtatLFqCpdab6FJ0WDVxqufpoarBtCLSCEiF5FDJC2ihGhYRF1FhNqRhUhwGJcfu2gRaGj1tmDzel6KI+B8aSpi0NGPMryKgUejFTHwuDKPwPNdoYiBx1J7DzzupToj8AS898uPXrQIPMHaQeAJFy9owedHv6oGoBhUNQilb9pSqqOqwehTsqqS0werGpSKG9VSlaoGmtJmZDktqTpATsw6jQCCTbk6AKZqVaVUKxsk26ZmkGyyaZts2qqabFqrA8mmG99k00qBybZJCJPNas0w2ayyYbL1OjJMtr7xTba+8U22vvFNtrHxTbZR2TDZRnWgZBu9qsFmrfoSplrHS5Rq7Y041U1vkmrNjYLNYNObpVpzo57qpreRaq0Zt1QrGycb1DFwstXH2E+TqdbeONmwzhJONqzEnGy46S3ZNs8QJxttxpBsVNkk2TbPmyQbVWJJNqpjkGTjWnU/r97l1vX5+HD/+bz+t8lPrzdr5i7+9fDp/Dk0XwJzLrl6fvp6fL57/HiMKxbb7aq/bqy/nZ6fPn37mF7dO/NXYD9kNfa5I92P6utWf/gHjU3d+Q==',
}

#This database can compare gestures the user makes to its stored     gestures
#and tell us if the user input matches any of them.
gestures = GestureDatabase()
for name, gesture_string in gesture_strings.items():
    gesture = gestures.str_to_gesture(gesture_string)
    gesture.name = name
    gestures.add_gesture(gesture)

class GestureBox(BoxLayout):

    def __init__(self, **kwargs):
        for name in gesture_strings:
            self.register_event_type('on_{}'.format(name))
        super(GestureBox, self).__init__(**kwargs)

    def on_left_to_right_line(self):
        pass

#To recognize a gesture, you’ll need to start recording each individual event in the
#touch_down handler, add the data points for each call to touch_move , and then do the
#gesture calculations when all data points have been received in the touch_up handler.

    def on_touch_down(self, touch):
        #create an user defined variable and add the touch coordinates
        touch.ud['gesture_path'] = [(touch.x, touch.y)]
        super(GestureBox, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        touch.ud['gesture_path'].append((touch.x, touch.y))
        super(GestureBox, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if 'gesture_path' in touch.ud:
            #create a gesture object
            gesture = Gesture()
            #add the movement coordinates
            gesture.add_stroke(touch.ud['gesture_path'])
            #normalize so thwu willtolerate size variations
            gesture.normalize()
            #minscore to be attained for a match to be true
            match = gestures.find(gesture, minscore=0.3)
            if match:
                print("{} happened".format(match[1].name))
                self.dispatch('on_{}'.format(match[1].name))
        super(GestureBox, self).on_touch_up(touch)