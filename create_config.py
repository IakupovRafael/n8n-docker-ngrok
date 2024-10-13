import yaml
import os

def prompt(message, default=None):
    """Prompt the user for input and return the response."""
    if default:
        response = input(f"{message} [default: {default}]: ").strip()
    else:
        response = input(f"{message}: ").strip()
    return response or default

def get_authtoken():
    """Prompt the user to enter the authtoken."""
    while True:
        authtoken = prompt("Enter the authtoken")
        if authtoken:
            return authtoken
        else:
            print("Authtoken is required. Please enter it.")

def get_endpoint_details(existing_urls):
    """Get endpoint details from the user."""
    while True:
        endpoint_name = prompt("Enter endpoint name (required)")
        if endpoint_name:
            break
        else:
            print("Endpoint name is required. Please enter it.")
    
    while True:
        port = prompt("Enter port (required)")
        if port:
            break
        else:
            print("Port is required. Please enter it.")

    # Protocol and URL are optional
    protocol = prompt("Enter protocol (optional)") or None
    
    url = None
    while url is None:
        url_input = prompt("Enter URL (optional) or type /existed to choose from existing").strip()
        if url_input == "":
            break
        elif url_input == "/existed" and existing_urls:
            print("Select an existing URL:")
            for idx, existing_url in enumerate(existing_urls, start=1):
                print(f"{idx}. {existing_url}")
            selection = prompt("Enter the number of the URL you want to use")
            if selection.isdigit() and 1 <= int(selection) <= len(existing_urls):
                url = existing_urls[int(selection) - 1]
            else:
                print("Invalid selection. Please try again.")
        else:
            url = url_input

    description = prompt("Enter description (optional)") or None
    
    # Create the endpoint configuration, omitting optional fields if they are None
    endpoint = {
        "name": endpoint_name,
        "upstream": {
            "url": port,
        }
    }
    if protocol:
        endpoint["upstream"]["protocol"] = protocol
    if url:
        endpoint["url"] = url
    if description:
        endpoint["description"] = description

    return endpoint

def add_section_to_config(config):
    """Add a new endpoint section to the configuration."""
    existing_urls = [ep["url"] for ep in config.get("endpoints", []) if ep.get("url")]
    endpoint = get_endpoint_details(existing_urls)
    if endpoint:
        config.setdefault("endpoints", []).append(endpoint)

def create_or_modify_config(filename):
    """Create a new configuration file or modify an existing one."""
    # Ensure the config directory exists
    config_dir = os.path.join(os.getcwd(), 'config')
    os.makedirs(config_dir, exist_ok=True)
    filepath = os.path.join(config_dir, filename)

    config = {}
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            config = yaml.safe_load(file) or {}
    
    if "agent" not in config:
        config["version"] = 3
        config["agent"] = {"authtoken": get_authtoken()}
    else:
        print("Configuration already has an authtoken.")
    
    while True:
        add_more = prompt("Do you want to add a new section? (yes/no)", default="no").lower()
        if add_more == 'yes':
            add_section_to_config(config)
        elif add_more == 'no':
            break
        else:
            print("Please answer yes or no.")
    
    with open(filepath, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    print(f"Configuration saved to {filepath}")

def main():
    """Main function to run the script."""
    filename = prompt("Enter the configuration file name (with .yml extension)", default="ngrok.yml")
    create_or_modify_config(filename)

if __name__ == "__main__":
    main()
