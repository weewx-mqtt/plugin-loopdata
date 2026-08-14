<!-- markdownlint-disable first-line-heading  -->

## Description

This is a template `readme` file.
It is meant to be used both in the repository display and the github pages.
This file is included from an `index.md` file in github pages.
It is displayed 'as-is' in the repository.
This means it must be 'native' markdown (or html).
Therefore the 'footer' is included directly in this file.
And the `index.md` file for github pages 'turns off the footer'.

**When using, remmber to update the URLs in the 'footer' and in 'additional information' below.**

## Preqrequisites

|Prerequisite                                                         |Version                  |
|---------------------------------------------------------------------|-------------------------|
|[WeeWX](https://www.weewx.com)                                       |5.0.0 or higher          |
|[Python](https://www.python.org)                                     |3.9.13 or higher         |
|[weewx-loopdata](https://github.com/chaunceygardiner/weewx-loopdata) |6.10 or higher           |

*Note:* Early versions of Python 3 may work, but have not been explicitly tested.

*Note:* Version 6.10 of weewx-loop data fixed an [issue](https://github.com/chaunceygardiner/weewx-loopdata/issues/15) with running version 5.2 and earlier of WeeWX.

## Installing

This extension is installed using the [weectl extension utility](https://www.weewx.com/docs/5.0/utilities/weectl-extension/).
The latest release can be installed with the invocation

```shell
weectl extension install https://github.com/weewx-mqtt/plugin-loopdata/archive/refs/tags/latest.zip
```

If a specific version is desired, the invocation would look like

```shell
weectl extension install https://github.com/weewx-mqtt/pligin-loopdata/archive/refs/tags/vX.Y.Z.zip
```

where X.Y.Z is the release.
The list of releases can be found at [https://github.com/weewx-mqtt/plugin-loopdata/releases](https://github.com/weewx-mqtt/plugin-loopdata/releases).

The version under development can be installed from the master branch using the following invocation

```shell
weectl extension install https://github.com/weewx-mqtt/plugin-loopdata/archive/master.zip
```

Where `master` is the branch name.

*Note:* WeeWX 'package' installs add the user that performed the install to the `weewx` group.
This means that this user should not need to use `sudo` to install the `MQTTPluginLoopData` extension.
**But** in order to for this update to the `weewx` group to take affect, the user has to have logged out/in at least once or use one of the other methods that can be found on the web

*Note:* WeeWX pip installs that install WeeWX into a `Python virtual environment`, must 'activate' the environment performing the install. A typical invocation would look like this.

```shell
source ~/weewx-venv/bin/activate
```

## Configuring

## Updating

---
**Getting Help**

For additional information see the [help](https://weewx-mqtt.github.io/plugin-loopdata/home/).

Feel free to
[open an issue](https://github.com/weewx-mqtt/plugin-loopdata/issues/new) or
[start a discussion in github](https://github.com/weewx-mqtt/plugin-loopdata/discussions/new).
When doing so, see
[Help! Posting to weewx user](https://github.com/weewx/weewx/wiki/) for information on capturing the log.

Since this plugin uses internal, unsupported, interfaces of [weewx-loopdata](https://github.com/chaunceygardiner/weewx-loopdata);
 please do not post to the WeeWX google group until we determined that is not a problem with MQTTLoopData.
