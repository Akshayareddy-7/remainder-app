# Remainder App

A simple Python-based reminder utility to help you schedule and manage reminders.

---

## Overview

This app allows users to store, schedule, and trigger reminders. Reminders are saved in a JSON file. It supports scheduling new reminders and checking existing ones. Aimed to be lightweight and easy to use.

---

## Features

- Schedule new reminders  
- View saved reminders  
- Uses a JSON file for storage (`reminders.json`)  
- Standalone Python script; no complex dependencies  

---

## Setup & Running

Here are the exact steps to run this on your local machine:

1. **Clone the repo**

    ```bash
    git clone https://github.com/Akshayareddy-7/remainder-app.git
    cd remainder-app
    ```

2. **(Optional) Setup virtual environment**

    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On Unix / MacOS:

        ```bash
        source venv/bin/activate
        ```

4. **Install any dependencies**  
   *(if you have any, else you can skip this)*  
   
   If you use `requirements.txt`, then:

    ```bash
    pip install -r requirements.txt
    ```

   If you don’t have that yet, you can manually install what’s needed.

5. **Run the app**

    ```bash
    python remainder_app.py
    ```

6. **Stopping / Exiting**

    Use `Ctrl + C` or close the terminal window.

---

## Usage

- To create a new reminder, follow the prompts (or check how input is handled in `remainder_app.py`)  
- Reminders are stored in `reminders.json`  
- Check/change `reminders.json` manually if needed  

---

## Contributing

Feel free to open issues, suggest improvements, or contribute new features. Some ideas:

- Add a GUI  
- Add recurring reminders  
- Better date/time parsing  
- Send notifications  



