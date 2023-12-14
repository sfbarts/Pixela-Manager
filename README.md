<!-- PROJECT LOGO -->
<br />
<div align="center">
    <img src="https://ik.imagekit.io/iWish/pm_logo.png?updatedAt=1702310672199" alt="pixela manager logo">

<h3 align="center">Pixela Manager</h3>
</div>

<!-- ABOUT THE PROJECT -->
## About The Project

Pixela Manager is a desktop GUI app that allows Pixela user's to manage and edit their graphs. 
It is particularly benefical to those that don't know how to work with APIs, don't feel comfortable with a CLI environment or 
those that simply prefer the ease of use of a graphical user interface.

It was built using Python 3.10 and PyQt6

## Usage
At the moment, Pixela Manager can only be run using python and it only has been tested in a windows environment.

### Using Python
1. Fork the project
2. Clone it to your local machine
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Pixela Manager relies on "libvips 8.14". If you don't have it installed on your machine, download windows binaries following https://www.libvips.org/install.html
   
    - You might need to change line 12 from "pixela_manager_main.py" to point to the folder where you installed libvips.
      
   ```python
   os.environ['PATH'] += r";C:\path\to\libvips"
   ```
5. Run main.py
```bash
python main.py
```


## Limitations
The manager is still bound to Pixela's policies.
- Latency is expected because of the 25% request rejection policy.

## Features coming soon
- Pixel details caching for faster response.
- Windows .exe



