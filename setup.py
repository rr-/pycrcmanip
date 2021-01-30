from distutils.core import Extension, setup


def main():
    setup(
        name="crcmanip",
        version="1.0.0",
        description="CRC manipulator",
        author="rr-",
        author_email="rr-@sakuya.pl",
        entry_points={"console_scripts": ["crcmanip = crcmanip.__main__:cli"]},
        ext_modules=[Extension("crcmanip.fastcrc", ["crcmanip/fastcrc.c"])],
        install_requires=["tqdm", "click"],
        tests_require=["pytest"],
    )


if __name__ == "__main__":
    main()
