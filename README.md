# ableton-shell
Easy, fast iteration and control of the Ableton Live Python API

### Install

Close Live, clone this repo, then from its dir (Mac OS X):
```bash
for live_dir in "$(find /Applications/Ableton* -name 'MIDI Remote Scripts')"; do
mkdir "$live_dir/Shellicopter"
for f in *.py ; do ln -s "$(pwd)/$f" "$live_dir/Shellicopter/$f" ; done ; done
```

Open Live -> Preferences -> Link MIDI, select Shellicopter in any Control Surface column cell.