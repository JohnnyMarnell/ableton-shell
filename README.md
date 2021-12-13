# ableton-shell
Easy, fast iteration and control of the Ableton Live Python API

### Use

Install `socat` if not already (`brew install socat`).
Start Live (with this Control Surface enabled).
Then:
```bash
➜  ~ socat readline TCP:localhost:10141
Welcome to Ableton Python Shell :)
>>> self
<Shellicopter.AbletonShellControlSurface.AbletonShellControlSurface object at 0x124d5eb38>
>>> self.c_instance.song()
<Song.Song object at 0x16f594578>
>>> self.c_instance.song().tracks
<Base.Vector object at 0x1232b7db0>
>>> [t.name for t in self.c_instance.song().tracks]
['Drums', 'Bass', 'Keys', '4-Audio', '5-Audio']
>>>
```

### Install

Close Live, clone this repo, then from its dir (Mac OS X):
```bash
for live_dir in "$(find /Applications/Ableton* -name 'MIDI Remote Scripts')"; do
mkdir "$live_dir/Shellicopter"
for f in *.py ; do ln -s "$(pwd)/$f" "$live_dir/Shellicopter/$f" ; done ; done
```

Open Live -> Preferences -> Link MIDI, select Shellicopter in any Control Surface column cell.