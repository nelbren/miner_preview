# ⛏️ miner_preview

[![](images/python.svg)](https://python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![](images/pylint.svg)](https://pylint.org/)
[![Donate with Ethereum](https://en.cryptobadges.io/badge/micro/0x0892c9b9b58ad5a7878d5dcd4da4ee72109c32c6)](https://en.cryptobadges.io/donate/0x0892c9b9b58ad5a7878d5dcd4da4ee72109c32c6)

### Get 💰 wallet 📈 balance from ☁️[Cloudatcost](https://www.cloudatcost.com/)  ⛏️ mining 🚧 process.

---

## 💻 Example of output
![](images/miner_preview.png)

---

## 🔩 Install

1. **Get from github**

    - Clone the project
        ```bash
        git clone https://github.com/nelbren/miner_preview.git
        ```

2. **Configure your credentials**
    - Take a copy of config
        - 🚪 Windows
            ```bash
            copy secret.cfg.EXAMPLE .secret.cfg
            ```

        - 🐧 Linux | 🍎  Mac      
            ```bash
            cp secret.cfg.EXAMPLE .secret.cfg
            ```
    - Change the data inside of `.secret.cfg`
        |Key|Value|Description|
        |:--|:--|:--|
        |**USERNAME**|your username|Credentials of access|
        |**PASSWORD**|your password|Credentials of access|
        |**CODE_2FA**|secret code 2FA|Credentials of access|
        |**GOAL_USD**|amount of usd|Goal in dollars|
        |**GOAL_BTC**|amount of btc|Goal in bitcoin|

3. **Install python and modules**
    
    - Please install **python** and **pip**
    
    - Install modules
        ```bash
        install.bat.bash
        ```

4. **Run the script**
    ```bash
    python preview.py
    ```

5. **Feedback:** 
   - Send suggestions, comments, etc. to: nelbren@nelbren.com

---

### 🔜 **TODO:**
- [ ] Graph from data
- [ ] Others reports
