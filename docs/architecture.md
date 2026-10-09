# Architecture
Each Pi serves its own JSON sensor record at /status on LAN TCP8088. Each configured peer polls /status; network policy ignores replay records for five seconds and expires missing nodes. RGB red means missing/stale peer, blue means any fresh room door is open below 50 lux, green means no such event. Communication stays on the private WLAN; no cloud dependency or internet API.
