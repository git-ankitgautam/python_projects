TITLE  = "Vlc player - Kate"
USEADS = False
DEBUG  = False

import os
import sys
import wx
import vlc

if DEBUG: import wx.lib.mixins.inspection

class MyApp(wx.App):

    def OnInit(self):
        self.frame = MyFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

class MyFrame(wx.Frame):

    def __init__(self):

        super().__init__(None, wx.ID_ANY)

        self.SetSize((500, 500))

        #Create display elements
        self.pnlVideo    = wx.Panel (self, wx.ID_ANY)
        self.sldPosition = wx.Slider(self, wx.ID_ANY, value=0, minValue=0, maxValue=1000)
        self.btnOpen     = wx.Button(self, wx.ID_ANY, "Open")
        self.btnPlay     = wx.Button(self, wx.ID_ANY, "Play")
        self.btnStop     = wx.Button(self, wx.ID_ANY, "Stop")
        self.btnMute     = wx.Button(self, wx.ID_ANY, "Mute")
        self.sldVolume   = wx.Slider(self, wx.ID_ANY, value=50, minValue=0, maxValue=200)
        self.timer       = wx.Timer (self)

        #Set display element properties and layout
        self.__set_properties()
        self.__do_layout()

        #Create event handlers
        self.Bind(wx.EVT_BUTTON, self.btnOpen_OnClick,   self.btnOpen)
        self.Bind(wx.EVT_BUTTON, self.btnPlay_OnClick,   self.btnPlay)
        self.Bind(wx.EVT_BUTTON, self.btnStop_OnClick,   self.btnStop)
        self.Bind(wx.EVT_BUTTON, self.btnMute_OnClick,   self.btnMute)
        self.Bind(wx.EVT_SLIDER, self.sldVolume_OnSet,   self.sldVolume)
        self.Bind(wx.EVT_SLIDER, self.sldPosition_OnSet, self.sldPosition)
        self.Bind(wx.EVT_TIMER , self.OnTimer,           self.timer) 

        self.Bind(wx.EVT_CLOSE , self.OnClose)

        #Create vlc objects and link the player to the display panel
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.pnlVideo.GetHandle())

        self.LoadConfig()

        if DEBUG: wx.lib.inspection.InspectionTool().Show()

    def __set_properties(self):
        if DEBUG: print("__set_properties")
        self.SetTitle(TITLE)
        self.root = os.path.expanduser("~")
        self.file = ""
        self.pnlVideo.SetBackgroundColour(wx.BLACK)
        self.sldVolume_OnSet(40)

    def __do_layout(self):
        if DEBUG: print("__do_layout")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)

        sizer_1.Add(self.pnlVideo, 1, wx.EXPAND, 0)
        sizer_1.Add(self.sldPosition, 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        sizer_2.Add(self.btnOpen, 0, 0, 0)
        sizer_2.Add(self.btnPlay, 0, 0, 0)
        sizer_2.Add(self.btnStop, 0, 0, 0)
        sizer_2.Add(80,23) #spacer
        sizer_2.Add(self.btnMute, 0, 0, 0)
        sizer_2.Add(self.sldVolume, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)

        self.Layout()

    def LoadConfig(self):
        """Load the settings from the previous run"""
        if DEBUG: print("LoadConfig")

        if USEADS: self.config = __file__ + ':config'
        else:      self.config = os.path.splitext(__file__)[0] + ".ini"

        try:
            with open(self.config,'r') as file:
                for line in file.read().splitlines():
                    if DEBUG: print(line)
                    exec(line)
        except: pass

    def SaveConfig(self):
        """Save the current settings for the next run"""
        if DEBUG: print("SaveConfig")

        x,y = self.GetPosition()
        w,h = self.GetSize()
        vol = self.sldVolume.GetValue()

        with open(self.config,'w') as file:
            file.write('self.SetPosition((%d,%d))\n' % (x, y))
            file.write('self.SetSize((%d,%d))\n'     % (w, h))
            file.write('self.sldVolume_OnSet(%d)\n'  % (vol))
            file.write('self.root = "%s"' % self.root.replace("\\","/"))

    def OnClose(self, event):
        """Clean up, save settings, and exit"""
        if DEBUG: print(f'OnClose {event=}')
        self.SaveConfig()
        sys.exit()

    def btnOpen_OnClick(self, event):
        """Prompt for, load, and play a video file"""
        if DEBUG: print(f'btnOpen_OnClick {event=}')

        #Stop any currently playing video
        self.btnStop_OnClick(None)

        #Display file dialog
        dlg = wx.FileDialog(self, "Select a file", self.root, "", "*.*", 0)

        if dlg.ShowModal() == wx.ID_OK:
            dir  = dlg.GetDirectory()
            file = dlg.GetFilename()

            self.root = dir

            self.media = self.instance.media_new(os.path.join(dir, file))
            self.player.set_media(self.media)

            if (title := self.player.get_title()) == -1:
                title = file
            self.SetTitle(title)

            #Play the video
            self.btnPlay_OnClick(None)

    def btnPlay_OnClick(self, event): 
        """Play/Pause the video if media present"""
        if DEBUG: print(f'btnPlay_OnClick {event=}')

        if self.player.get_media():            
            if self.player.get_state() == vlc.State.Playing:
                #Pause the video
                self.player.pause()
                self.btnPlay.Label = "Play"
            else:
                #Start or resume playing
                self.player.play()
                self.timer.Start()
                self.btnPlay.Label = "Pause"

    def btnStop_OnClick(self, event):
        """Stop playback"""
        if DEBUG: print(f'btnStop_OnClick {event=}')
        self.timer.Stop()
        self.player.stop()
        self.btnPlay.Label = "Play"
        self.sldPosition_OnSet(0)

    def btnMute_OnClick(self, event):
        """Mute/Unmute the audio"""
        if DEBUG: print(f'btnMute_OnClick {event=}')
        self.player.audio_set_mute(not self.player.audio_get_mute())
        self.btnMute.Label = "Unute" if self.player.audio_get_mute() else "Mute"

    def sldVolume_OnSet(self, event):
        """Adjust volume"""
        if DEBUG: print(f'sldVolume_OnSet {event=}')

        if type(event) is int:
            #Use passed value as  new volume
            volume = event
            self.sldVolume.SetValue(volume)
        else:
            #Use slider value as new volume
            volume = self.sldVolume.GetValue()

    def sldPosition_OnSet(self, event):
        """Select a new position for playback"""
        if DEBUG: print(f'sldPosition_OnSet {event=}')

        if type(event) is int:
            #Use passed value as new position (passed value = 0 to 100)
            newpos = event / 100.0
            self.sldPosition.SetValue(int(self.player.get_length() * newpos))
        else:
            #Use slider value to calculate new position from 0.0 to 1.0
            newpos = self.sldPosition.GetValue()/self.player.get_length()

        self.player.set_position(newpos)

    def GetAspect(self):
        """Return the video aspect ratio w/h if available, or 4/3 if not"""
        width,height = self.player.video_get_size()
        return 4.0/3.0 if height == 0 else width/height

    def OnTimer(self, event):
        """Update the position slider"""

        if self.player.get_state() == vlc.State.Ended:
            self.btnStop_OnClick(None)
            return

        if self.player.get_state() == vlc.State.Playing:
            length = self.player.get_length()
            self.sldPosition.SetRange(0, length)
            time = self.player.get_time()
            self.sldPosition.SetValue(time)
            #Force volume to slider volume (bug)
            self.player.audio_set_volume(self.sldVolume.GetValue())

        #Ensure display is same aspect as video
        aspect = self.GetAspect()
        width,height = self.GetSize()
        newheight = 75 + int(width/aspect)
        if newheight != height:
            self.SetSize((width,newheight))

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()