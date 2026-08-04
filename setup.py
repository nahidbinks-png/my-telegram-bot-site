from setuptools import setup, find_packages

setup(
    name="my_telegram_bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pyTelegramBotAPI",
        "supabase",
        "flask",
        "yt-dlp",
        "requests",
        "beautifulsoup4",
    ],
)
