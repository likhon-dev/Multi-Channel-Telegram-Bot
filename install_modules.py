import subprocess
import sys

def install_modules():
    modules = [
        'python-telegram-bot==13.7',
        'pytz'
    ]

    for module in modules:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])

if __name__ == '__main__':
    install_modules()
    print("All required modules have been installed successfully.")

