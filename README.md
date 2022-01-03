# here_weather

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to integrate with [HERE Destination Weather API][here_destination_weather_api]._

**Weather**

![example][exampleimg]

**Sensors**

![moonphases][moonphases_img]

## Setup

You need to register for an API key (REST & XYZ HUB API/CLI) by following the instructions [here](https://developer.here.com/tutorials/getting-here-credentials/).

HERE offers a Freemium Plan which includes 250,000 free Transactions per month. For the Destination Weather API, one transaction equals one request.

By default HERE will deactivate your account if you exceed the free Transaction limit for the month. You can add payment details to re-enable your account as described [here](https://knowledge.here.com/csm_kb?id=public_kb_csm_details&number=KB0016434).

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `here_weather`.
4. Download _all_ the files from the `custom_components/here_weather/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "HERE Destination Weather"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/here_weather/translations/en.json
custom_components/here_weather/translations/de.json
custom_components/here_weather/__init__.py
custom_components/here_weather/config_flow.py
custom_components/here_weather/const.py
custom_components/here_weather/manifest.json
custom_components/here_weather/sensor.py
custom_components/here_weather/utils.py
custom_components/here_weather/weather.py
```

## Additional entities

The integration provides the following four modes:

* **Astronomy**: Sunrise, Sunset and Moonphase
* **Hourly**: Weather forecast in an hourly format
* **Daily**: Weather forecast in a dailyformat
* **Daily Simple**: Like Daily but with high/low temp, UV-index and pressure
* **Observation**: Detailed precipitation for the next 24h

By default only the Daily Simple weather and sensor entities are enabled.
To enable more entities go to the entities tab and enable them by hand:

![disabled_entities_img][disabled_entities_img]
![enable_entity_img][enable_entity_img]

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

<a href="https://www.buymeacoffee.com/eifinger" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/black_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a><br>

[here_destination_weather_api]: https://developer.here.com/documentation/destination-weather/dev_guide/topics/overview.html
[buymecoffee]: https://www.buymeacoffee.com/eifinger
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/eifinger/hass-here-weather.svg?style=for-the-badge
[commits]: https://github.com/eifinger/hass-here-weather/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: img/here_weather_7days_forecast.png
[disabled_entities_img]: img/here_weather_disabled_entities.png
[enable_entity_img]: img/here_weather_enable_entity.png
[moonphases_img]: img/here_weather_moonphases.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/eifinger/hass-here-weather.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Kevin%20Stillhammer%20%40eifinger-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/eifinger/hass-here-weather.svg?style=for-the-badge
[releases]: https://github.com/eifinger/hass-weenect/releases
