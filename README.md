# BootAnimationMaker -- Android Boot Animation Magisk Module Maker

-> [中文](README_CN.md) <-

A tool to combine the images (png, jpg ...) and motion images (gif) to make Android boot animations, and package them into a Magisk module

## Environment

### Python and Python Dependencies

Please ensure that **Python version >= 3.7** because new features such as dataclass are used.

```txt
# Python dependencies

pillow   >= 5.3.0
tqdm     >= 4.28.1
requests >= 2.20.1
colorama >= 0.4.1
click    >= 7.0
pyyaml   >= 3.13
```

Please check these dependencies, or install them using `pip install-r requirements.txt`.

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

Get the script. Download or use `git`

```sh
git clone https://github.com/Zarcher0/BootAnimationMaker.git
```

Open Terminal(PowerShell) in the script folder

Prepare the images witch to be made into animations. Then it is suggested to place them in a subfolder under the script folder, and create a new `config.yml` file in it. Its format refers to [config_template.yml](config_template.yml).

Then run `run.py'.

```sh
python run.py # The default configuration file path is "./config.yml"

# Or use "--config" to specify a configuration path

python run.py --config xxxxx
```

See the `example` folder for several reference examples.

For example, to run `example/1`

```sh
python run.py --config ./example/1/config.yml
```

After generating you can find the Magisk module and preview gif in `./export` directory.

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












