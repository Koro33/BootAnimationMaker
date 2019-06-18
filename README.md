# BootAnimationMaker -- Android Boot Animation Magisk Module Maker

-> [中文](README_CN.md) <-

A tool to combine the images (png, jpg ...) and motion images (gif) to make Android boot animations, and package them into a Magisk module

## Environment

### Python and Python Dependencies

```auto
python    >= 3.6

pillow    >= 5.3.0
tqdm      >= 4.28.1
requests  >= 2.20.1
colorama  >= 0.4.1
click     >= 7.0
pyyaml    >= 3.13
printtags >= 1.4
```

This project uses `poetry` for dependency management. Run `poetry install` in the script root directory to install the virtual environment and dependencies, and run `poetry run python run.py` to run the script.

### Other Dependencies

This script also uses third-party software such as [gifsicle](https://www.lcdf.org/gifsicle/), [pngquant](https://pngquant.org/). Please use the corresponding methods to install the software package according to the platforms.

* Linux

  Install `gifsicle`, `pngquant` using package manager

* Windows

  For convenience `Gifsicle`, `pngquant` is included in `bin` folder by default. No additional installation is required. If you want to change the version, you must ensure that `gifsicle.exe`, `pngquant.exe` has the same path structure as the current one.

* Mac

  It is temporarily not supported. Because there is no Mac device for me to test.

  Welcome `pull requests`.

## Getting Started

* Get the script. Download or use `git clone`

    ```sh
    git clone https://github.com/Zarcher0/BootAnimationMaker.git
    ```

* Prepare the material which to made animations. Put them into a subfolder(new) under the script root directory, and create a new `config.yml` file in it. Its format refers to [config_template.yml](config_template_CN.yml).

* In root folder of the script, Then run `python run.py --config xxxx` or `poetry run python run.py --config xxxx` (if uses poetry).

> when run `python run.py`, the default configuration file path is `./config.yml`，use `--config` to specify a configuration path `python run.py --config xxxxx`

Look at the `example` folder for several reference examples.

For example, to run `example/1`

```sh
python run.py --config ./example/1/config.yml
```

After generating you can find the Magisk module and its preview gif in `./export` directory.

![Screenshot0](./example/Screenshot0.png)

> Note: If the image path in the `config.yml` file is a relative path, the default is relative to the running environment. It is recommended to use an absolute path to avoid errors.

## Demo

> **Copyright Statement**: All the pictures are from the Internet. They are only for technical testing and display. Please do not use them for any commercial purpose. If there is any infringement, please contact me to delete.

<table>
    <tr>
        <td><center><img src="./example/1/preview0.gif" >Animation 1</center></td>
        <td><center><img src="./example/2/preview0.gif" >Animation 2</center></td>
        <td><center><img src="./example/3/preview0.gif" >Animation 3</center></td>
        <td><center><img src="./example/4/preview0.gif" >Animation 4</center></td>
    </tr>
</table>

<table>
    <tr>
        <td><center><img src="./example/5/preview0.gif" >Animation 5 part 0</center></td>
        <td><center><img src="./example/5/preview1.gif" >Animation 5 part 1</center></td>
        <td><center><img src="./example/6/preview0.gif" >Animation 6 part 0</center></td>
        <td><center><img src="./example/6/preview1.gif" >Animation 6 part 1</center></td>
    </tr>
</table>

## Compatibility

It should be compatible with most models. For some models such as Samsung, its directory structure is inconsistent with others. It is not recommended for them to use this script

## license

[Apache Licnese 2.0](LICENSE)












