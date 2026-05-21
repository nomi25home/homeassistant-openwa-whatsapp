# OpenWA WhatsApp API Add-on

This add-on installs the OpenWA API server, providing a high-performance gateway to send and receive WhatsApp messages.

## Integration
To use this add-on, you must also install the **OpenWA WhatsApp** custom integration via HACS.

1. Install this add-on.
2. Configure the **API Master Key** in the add-on options.
3. Start the add-on.
4. In Home Assistant, go to **Settings** $\rightarrow$ **Devices & Services** $\rightarrow$ **Add Integration** $\rightarrow$ **OpenWA WhatsApp**.
5. Use `http://core-openwa-whatsapp:2785` (or the IP of your HA instance) as the Base URL.

## Configuration
- **API Master Key**: Your unique key to authenticate requests to the API.
- **Log Level**: Adjust the verbosity of the logs.
- **Engine Type**: The WhatsApp engine used by OpenWA.

## Requirements
- A valid WhatsApp account authenticated via the OpenWA session manager.
