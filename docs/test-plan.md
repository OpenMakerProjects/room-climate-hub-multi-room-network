# Test plan
CI executes unittest replay/type/staleness/coordination tests, Python compilation, two actual HTTP simulation processes polling one another, PNG transport and completion validators. Hardware not tested: repeat with two Pi Zero2W boards, check BH1750 I2C address and lux, reed polarity, each RGB channel, peer outage and graceful shutdown. Never connect locks or mains.
